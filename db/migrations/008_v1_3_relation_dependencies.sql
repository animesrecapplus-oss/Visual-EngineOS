-- V1.3 semantic relation dependency contract.
-- Relation direction is explicit/data-driven; unknown relation types remain neutral.

CREATE TABLE IF NOT EXISTS relation_dependency_rules (
    relation_type TEXT PRIMARY KEY,
    dependency_direction TEXT NOT NULL,
    CHECK (relation_type <> ''),
    CHECK (dependency_direction IN ('none', 'source_to_target', 'target_to_source', 'bidirectional'))
);

INSERT INTO relation_dependency_rules (relation_type, dependency_direction) VALUES
    ('STRUCTURAL', 'source_to_target'),
    ('SPATIAL', 'source_to_target'),
    ('ANATOMICAL', 'source_to_target'),
    ('GEOMETRIC', 'source_to_target'),
    ('CONTACT', 'bidirectional'),
    ('OCCLUSION', 'source_to_target'),
    ('ATTACHMENT', 'source_to_target'),
    ('DEFORMATION', 'source_to_target'),
    ('CAUSAL', 'source_to_target'),
    ('EXPRESSIVE', 'source_to_target'),
    ('SEMANTIC', 'source_to_target')
ON CONFLICT (relation_type) DO UPDATE SET dependency_direction = EXCLUDED.dependency_direction;

CREATE INDEX IF NOT EXISTS idx_relation_dependency_rules_direction
    ON relation_dependency_rules(dependency_direction, relation_type);
