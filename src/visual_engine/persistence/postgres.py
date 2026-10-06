from __future__ import annotations

from typing import Any, Protocol
import json


def _json(value: Any) -> str:
    """Encode JSONB payloads deterministically and reject non-finite/non-JSON values."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)

from visual_engine.components.common.meta import (
    AppearanceLayer, Component, Constraint, ConstraintKind, Profile, Relation, StateLayer,
)
from visual_engine.runtime.graph import RuntimeGraph

from .migrations import PostgresMigrationRunner
from .serialization import component_from_payload, component_payload, parameter_payload


class EntityRepository(Protocol):
    def save_entity(self, record: dict[str, Any]) -> None: ...
    def load_entity(self, entity_id: str) -> dict[str, Any] | None: ...
    def save_component_tree(self, record: dict[str, Any], root: Component) -> int: ...
    def load_component_tree(self, entity_id: str) -> tuple[dict[str, Any], Component, int] | None: ...


class PostgresEntityRepository:
    """PostgreSQL persistence boundary; the renderer never queries the database.

    The generic vertical slice writes the authoring graph as one transaction: the entity
    record, version snapshot, component/parameter/anchor projection, and relationship
    tables either commit together or none of them become visible. Relational columns are
    used for stable/queryable facts; extensible transform/visual/geometry contracts remain
    JSONB metadata instead of forcing a schema migration for every new visual field.
    """

    def __init__(self, dsn: str, *, migration_dir: str | None = None):
        if not dsn:
            raise ValueError("PostgreSQL DSN must not be empty")
        self.dsn = dsn
        self.migration_dir = migration_dir

    def _connect(self):
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("Install visual-engine[postgres] to use PostgreSQL persistence") from exc
        return psycopg.connect(self.dsn)

    def migrate(self) -> tuple[str, ...]:
        """Bring the database to the latest repository migration."""
        return PostgresMigrationRunner(self._connect, self.migration_dir).migrate()

    def current_schema_version(self) -> str | None:
        return PostgresMigrationRunner(self._connect, self.migration_dir).current_version()

    def save_entity(self, record: dict[str, Any]) -> None:
        required = {"entity_id", "schema_version"}
        missing = required - set(record)
        if missing:
            raise ValueError(f"Entity record missing required fields: {sorted(missing)}")
        payload = _json(record)
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO entity_instances(entity_id, schema_version, payload) VALUES (%s,%s,%s::jsonb) "
                    "ON CONFLICT(entity_id) DO UPDATE SET schema_version=EXCLUDED.schema_version, payload=EXCLUDED.payload",
                    (record["entity_id"], record["schema_version"], payload),
                )
            conn.commit()

    def load_entity(self, entity_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT payload FROM entity_instances WHERE entity_id=%s", (entity_id,))
                row = cur.fetchone()
        return row[0] if row else None

    def save_component_tree(self, record: dict[str, Any], root: Component) -> int:
        """Persist one complete generic component graph and create an immutable version.

        The runtime graph is compiled first so malformed topology is rejected before any
        SQL is issued. A single database transaction then replaces the entity's current
        relational projection and records a monotonically increasing entity version.
        """
        required = {"entity_id", "schema_version", "engine_version", "seed", "root_kind"}
        missing = required - set(record)
        if missing:
            raise ValueError(f"Entity record missing required fields: {sorted(missing)}")
        graph = RuntimeGraph.from_component(root)
        if root.id not in graph.nodes:
            raise ValueError("Root component is absent from compiled graph")
        if root.kind != record["root_kind"]:
            raise ValueError(
                f"Entity root kind mismatch: record={record['root_kind']!r}, component={root.kind!r}"
            )
        if isinstance(record["seed"], bool) or not isinstance(record["seed"], int):
            raise ValueError("Entity seed must be an integer")

        entity_id = record["entity_id"]
        entity_payload = _json(record)
        components = tuple(graph.nodes[node_id].component for node_id in graph.nodes)
        child_orders = {
            child.id: index
            for parent in components
            for index, child in enumerate(parent.children)
        }

        with self._connect() as conn:
            with conn.cursor() as cur:
                # The upsert locks the entity row for this transaction, serializing version
                # allocation for concurrent writers without a process-local lock.
                cur.execute(
                    "INSERT INTO entity_instances(entity_id, schema_version, payload) VALUES (%s,%s,%s::jsonb) "
                    "ON CONFLICT(entity_id) DO UPDATE SET schema_version=EXCLUDED.schema_version, payload=EXCLUDED.payload",
                    (entity_id, record["schema_version"], entity_payload),
                )
                # Lock the entity row itself before allocating the next immutable version.
                # ``FOR UPDATE`` on an aggregate query is rejected by PostgreSQL, so the
                # lock and MAX query are deliberately separate statements.
                cur.execute("SELECT entity_id FROM entity_instances WHERE entity_id=%s FOR UPDATE", (entity_id,))
                cur.fetchone()
                cur.execute(
                    "SELECT COALESCE(MAX(version), 0) + 1 FROM entity_versions WHERE entity_id=%s",
                    (entity_id,),
                )
                version = int(cur.fetchone()[0])
                cur.execute(
                    "INSERT INTO entity_versions(entity_id, version, engine_version, seed, payload) "
                    "VALUES (%s,%s,%s,%s,%s::jsonb)",
                    (entity_id, version, record["engine_version"], record["seed"], entity_payload),
                )

                # Replace only this entity's projection. Foreign keys make the operation
                # safe, and the surrounding transaction prevents readers from observing
                # a half-written graph.
                cur.execute("DELETE FROM relations WHERE entity_id=%s", (entity_id,))
                cur.execute(
                    "DELETE FROM constraints WHERE component_id IN "
                    "(SELECT component_id FROM components WHERE entity_id=%s)", (entity_id,)
                )
                cur.execute(
                    "DELETE FROM profiles WHERE component_id IN "
                    "(SELECT component_id FROM components WHERE entity_id=%s)", (entity_id,)
                )
                cur.execute(
                    "DELETE FROM appearance_layers WHERE component_id IN "
                    "(SELECT component_id FROM components WHERE entity_id=%s)", (entity_id,)
                )
                cur.execute(
                    "DELETE FROM state_layers WHERE component_id IN "
                    "(SELECT component_id FROM components WHERE entity_id=%s)", (entity_id,)
                )
                cur.execute(
                    "DELETE FROM component_states WHERE component_id IN "
                    "(SELECT component_id FROM components WHERE entity_id=%s)", (entity_id,)
                )
                cur.execute("DELETE FROM components WHERE entity_id=%s", (entity_id,))

                type_ids: dict[str, int] = {}
                for component in components:
                    cur.execute(
                        "INSERT INTO component_types(name) VALUES (%s) "
                        "ON CONFLICT(name) DO UPDATE SET name=EXCLUDED.name "
                        "RETURNING component_type_id",
                        (component.kind,),
                    )
                    type_ids[component.kind] = int(cur.fetchone()[0])

                for component in components:
                    metadata = component_payload(component, child_order=child_orders.get(component.id))
                    cur.execute(
                        "INSERT INTO components(component_id, entity_id, parent_id, component_type_id, kind, parameters, anchors, metadata) "
                        "VALUES (%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb)",
                        (
                            component.id, entity_id, component.parent_id, type_ids[component.kind], component.kind,
                            _json(parameter_payload(component.parameters)),
                            _json({name: {"x": a.x, "y": a.y, "z": a.z} for name, a in component.anchors.items()}),
                            _json(metadata),
                        ),
                    )
                    for constraint in component.constraints:
                        cur.execute(
                            "INSERT INTO constraints(component_id,name,kind,expression,weight) VALUES (%s,%s,%s,%s,%s)",
                            (component.id, constraint.name, constraint.kind.value, constraint.expression, constraint.weight),
                        )
                    for profile in component.profiles.values():
                        cur.execute(
                            "INSERT INTO profiles(component_id,profile_type,name,values) VALUES (%s,%s,%s,%s::jsonb)",
                            (component.id, "generic", profile.name, _json(profile.values)),
                        )
                    for layer in component.appearance:
                        cur.execute(
                            "INSERT INTO appearance_layers(component_id,name,values,opacity) VALUES (%s,%s,%s::jsonb,%s)",
                            (component.id, layer.name, _json(layer.values), layer.opacity),
                        )
                    for state in component.state:
                        cur.execute(
                            "INSERT INTO component_states(component_id,state_name,enabled,priority,exclusive_group,conflicts,requires,values) "
                            "VALUES (%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb)",
                            (component.id, state.name, state.enabled, state.priority, state.group,
                             _json(list(state.conflicts)), _json(list(state.requires)),
                             _json(state.values)),
                        )
                for relation in graph.relations:
                    cur.execute(
                        "INSERT INTO relations(entity_id,source_id,relation_type,target_id,metadata) VALUES (%s,%s,%s,%s,%s::jsonb)",
                        (entity_id, relation.source_id, relation.relation_type, relation.target_id,
                         _json(relation.metadata)),
                    )
            conn.commit()
        return version

    def load_component_tree(self, entity_id: str) -> tuple[dict[str, Any], Component, int] | None:
        """Load one entity with bounded-query relational hydration (no N+1 SQL)."""
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT payload FROM entity_instances WHERE entity_id=%s", (entity_id,))
                entity_row = cur.fetchone()
                if entity_row is None:
                    return None
                cur.execute(
                    "SELECT entity_version_id, version FROM entity_versions WHERE entity_id=%s ORDER BY version DESC LIMIT 1",
                    (entity_id,),
                )
                version_row = cur.fetchone()
                version = int(version_row[1]) if version_row else 0
                cur.execute(
                    "SELECT component_id,parent_id,kind,parameters,anchors,metadata FROM components WHERE entity_id=%s",
                    (entity_id,),
                )
                component_rows = cur.fetchall()
                cur.execute(
                    "SELECT source_id,relation_type,target_id,metadata FROM relations WHERE entity_id=%s",
                    (entity_id,),
                )
                relation_rows = cur.fetchall()
                ids = [row[0] for row in component_rows]
                if ids:
                    cur.execute("SELECT component_id,name,kind,expression,weight FROM constraints WHERE component_id = ANY(%s)", (ids,))
                    constraint_rows = cur.fetchall()
                    cur.execute("SELECT component_id,profile_type,name,values FROM profiles WHERE component_id = ANY(%s)", (ids,))
                    profile_rows = cur.fetchall()
                    cur.execute("SELECT component_id,name,values,opacity FROM appearance_layers WHERE component_id = ANY(%s)", (ids,))
                    appearance_rows = cur.fetchall()
                    cur.execute("SELECT component_id,state_name,enabled,priority,exclusive_group,conflicts,requires,values FROM component_states WHERE component_id = ANY(%s)", (ids,))
                    state_rows = cur.fetchall()
                else:
                    constraint_rows = profile_rows = appearance_rows = state_rows = []

        components: dict[str, Component] = {}
        child_orders: dict[str, int] = {}
        for cid, parent_id, kind, parameters, anchors, metadata in component_rows:
            components[cid] = component_from_payload(cid, kind, parent_id, parameters, anchors, metadata)
            order = metadata.get("persistence", {}).get("child_order")
            if isinstance(order, int):
                child_orders[cid] = order
        if not components:
            raise RuntimeError(f"Entity {entity_id} has no persisted components")

        for cid, name, kind, expression, weight in constraint_rows:
            components[cid].add_constraint(Constraint(name, ConstraintKind(kind), expression, weight))
        for cid, _profile_type, name, values in profile_rows:
            components[cid].profiles[name] = Profile(name, dict(values))
        for cid, name, values, opacity in appearance_rows:
            components[cid].add_appearance(AppearanceLayer(name, dict(values), opacity))
        for cid, name, enabled, priority, group, conflicts, requires, values in state_rows:
            components[cid].add_state(StateLayer(name, dict(values), enabled, priority, group, tuple(conflicts), tuple(requires)))
        for source_id, relation_type, target_id, metadata in relation_rows:
            if source_id not in components or target_id not in components:
                raise RuntimeError(
                    f"Entity {entity_id} contains a relation to a missing component: "
                    f"{source_id!r} -> {target_id!r}"
                )
            components[source_id].relations.append(Relation(source_id, relation_type, target_id, dict(metadata)))

        roots = [component for component in components.values() if component.parent_id is None]
        if len(roots) != 1:
            raise RuntimeError(f"Entity {entity_id} must have exactly one root, found {len(roots)}")
        root = roots[0]
        for component in components.values():
            if component.parent_id is not None:
                parent = components.get(component.parent_id)
                if parent is None:
                    raise RuntimeError(f"Entity {entity_id} references missing parent {component.parent_id}")
                parent.children.append(component)
        for parent in components.values():
            parent.children.sort(key=lambda child: (child_orders.get(child.id, 2**31 - 1), child.id))
        # Recompile after hydration to prove the persisted topology is internally valid.
        RuntimeGraph.from_component(root)
        return entity_row[0], root, version

