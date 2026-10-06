from .identity import stable_digest
from .graph import RuntimeGraph, RuntimeNode
from .catalog import CompiledProfileCache, ProfileKey

__all__ = ["RuntimeGraph", "RuntimeNode", "CompiledProfileCache", "ProfileKey"]
from .contract import resolve_component, resolve_component_contract
from .resolution_context import ResolutionContext
from .resolved_component import ResolutionTrace, ResolvedComponent
from visual_engine.components.common.visual_contract import ResolvedVisualContract
__all__ += ["resolve_component", "resolve_component_contract", "ResolvedComponent", "ResolutionContext", "ResolutionTrace", "ResolvedVisualContract"]
from .provenance import ResolutionProvenance, ResolutionStep
from .versioning import VersionStamp, ResolutionFingerprint, InvalidationReason, stable_digest, component_fingerprint, dependency_fingerprint, context_fingerprint, resolution_fingerprint, invalidation_reasons
from .version_policy import ENGINE_VERSION, SCHEMA_VERSION, RESOLUTION_VERSION, VersionPolicy, CURRENT_VERSION_POLICY
__all__ += ["ResolutionProvenance", "ResolutionStep", "VersionStamp", "ResolutionFingerprint", "InvalidationReason", "stable_digest", "component_fingerprint", "dependency_fingerprint", "context_fingerprint", "resolution_fingerprint", "invalidation_reasons", "ENGINE_VERSION", "SCHEMA_VERSION", "RESOLUTION_VERSION", "VersionPolicy", "CURRENT_VERSION_POLICY"]
from .state_policy import StateActivation, collect_state_activations, resolve_state_activations, resolve_states
from .effects import VisualEffect, sort_effects, resolve_effects
from .effect_color import (
    EFFECT_COLOR_OPERATION_ID, EFFECT_COLOR_OPERATION_VERSION, EFFECT_COLOR_CALCULATION_SPACE,
    EffectColorResult, apply_effect_color,
)
__all__ += [
    "StateActivation", "collect_state_activations", "resolve_state_activations", "resolve_states",
    "VisualEffect", "sort_effects", "resolve_effects",
    "EFFECT_COLOR_OPERATION_ID", "EFFECT_COLOR_OPERATION_VERSION",
    "EFFECT_COLOR_CALCULATION_SPACE", "EffectColorResult", "apply_effect_color",
]
from .state_policy import StateDecision, resolve_states_with_decisions, resolve_state_activations_with_decisions
__all__ += ["StateDecision", "resolve_states_with_decisions", "resolve_state_activations_with_decisions"]
from .dependencies import RelationDependency, RelationDependencyIndex, build_relation_dependency_index, relation_direction, relation_effects
__all__ += ["RelationDependency", "RelationDependencyIndex", "build_relation_dependency_index", "relation_direction", "relation_effects"]
from .geometry_cache import GeometryCacheKey, GeometryCacheEntry, GeometryCacheStats, GeometryCache, geometry_input_payload, geometry_input_fingerprint, geometry_dependency_fingerprint, geometry_dependency_ids
from .resolution_cache import ResolutionCache, ResolutionCacheStats
__all__ += ["ResolutionCache", "ResolutionCacheStats"]
__all__ += ["GeometryCacheKey", "GeometryCacheEntry", "GeometryCacheStats", "GeometryCache", "geometry_input_payload", "geometry_input_fingerprint", "geometry_dependency_fingerprint", "geometry_dependency_ids"]
from .generators import GeometryGenerator, RegisteredGeometryGenerator, GeometryGeneratorRegistry
from .generation import GeometryGenerationResult, CachedGeometryGenerator
__all__ += ["GeometryGenerator", "RegisteredGeometryGenerator", "GeometryGeneratorRegistry", "GeometryGenerationResult", "CachedGeometryGenerator"]
from .geometry_transform import (
    GeometryTransformResolution,
    camera_matrix,
    local_transform_matrix,
    placement_matrix,
    resolve_geometry_contract,
    resolve_geometry_transform,
    resolve_local_to_world,
)
from .geometry_contract_transform import transform_geometry_contract
__all__ += [
    "GeometryTransformResolution", "camera_matrix", "local_transform_matrix", "placement_matrix",
    "resolve_geometry_contract", "resolve_geometry_transform", "resolve_local_to_world",
    "transform_geometry_contract",
]
from .semantic_regions import RegionKind, SemanticRegion, RegionMap, rectangle_region, polygon_region
from .coverage import DepthRelation, Occluder, RegionCoverage, CoverageResult, resolve_coverage
from .region_maps import (
    SemanticRegionProvider, RegisteredSemanticRegionProvider, SemanticRegionProviderRegistry,
    RegionMapResolution, generic_geometry_region_map, generic_region_provider, resolve_region_map,
)
__all__ += [
    "SemanticRegionProvider", "RegisteredSemanticRegionProvider", "SemanticRegionProviderRegistry",
    "RegionMapResolution", "generic_geometry_region_map", "generic_region_provider", "resolve_region_map",
]

from .region_geometry import (
    BooleanPolygon, RegionGeometry, primitive_to_region, path_to_region, geometry_to_region, region_to_contract,
)
from .visibility_boolean import (
    BooleanOperation, BooleanResult, boolean_operation, union_geometries,
    intersection_geometry, difference_geometry,
)
from .visibility import (
    VisibilityEventKind, AffectedRegionEvent, VisibilityRegionResult, VisibilityResult, resolve_visibility,
)
__all__ += [
    "BooleanOperation", "BooleanPolygon", "RegionGeometry", "BooleanResult",
    "VisibilityEventKind", "AffectedRegionEvent", "VisibilityRegionResult", "VisibilityResult",
    "primitive_to_region", "path_to_region", "geometry_to_region", "region_to_contract", "boolean_operation",
    "union_geometries", "intersection_geometry", "difference_geometry", "resolve_visibility",
]
from .consequences import (
    ConsequenceKind, ConsequenceRequest, ConsequenceRule, ConsequenceResolution,
    resolve_consequences, resolve_attribution_consequences,
)
__all__ += ["ConsequenceKind", "ConsequenceRequest", "ConsequenceRule", "ConsequenceResolution", "resolve_consequences", "resolve_attribution_consequences"]
from .placement_coverage import CoverageIntent
from .placement import (
    AnchorReference, DimensionConstraint, PlacementIntent,
    PlacementScaleMode, PlacementDepthRelation, PlacementSolution, resolve_placement,
)
__all__ += [
    "AnchorReference", "DimensionConstraint", "CoverageIntent", "PlacementIntent",
    "PlacementScaleMode", "PlacementDepthRelation", "PlacementSolution", "resolve_placement",
]
from .spatial_relationships import (
    RelationPlacementSpec, RelationPlacementResolution,
    compile_relation_placement, resolve_relation_placement, resolve_graph_placements,
)
__all__ += [
    "RelationPlacementSpec", "RelationPlacementResolution", "compile_relation_placement",
    "resolve_relation_placement", "resolve_graph_placements",
]
from .placement import resolve_placed_geometry
__all__ += ["resolve_placed_geometry"]
from .placement_constraints import (
    ConstraintStatus, ContainmentConstraint, ClearanceConstraint, NonPenetrationConstraint,
    PlacementConstraintSet, ConstraintCheck, ConstrainedPlacementSolution,
    validate_placement_constraints, resolve_constrained_placement,
)
__all__ += [
    "ConstraintStatus", "ContainmentConstraint", "ClearanceConstraint", "NonPenetrationConstraint",
    "PlacementConstraintSet", "ConstraintCheck", "ConstrainedPlacementSolution",
    "validate_placement_constraints", "resolve_constrained_placement",
]
from .spatial_relationships import resolve_relation_constrained_placement
__all__ += ["resolve_relation_constrained_placement"]
from .placement_visibility import PlacementVisibilityResolution, materialize_region_map, resolve_placement_visibility
__all__ += ["PlacementVisibilityResolution", "materialize_region_map", "resolve_placement_visibility"]
from .visibility_attribution import AttributionKind, OccluderAttribution, VisibilityAttributionResult, resolve_visibility_attribution
__all__ += ["AttributionKind", "OccluderAttribution", "VisibilityAttributionResult", "resolve_visibility_attribution"]
__all__ += ["PlacementVisibilityResolution", "materialize_region_map", "resolve_placement_visibility"]
from .consequence_aggregation import (
    AggregationMode, ConsequencePolicy, ConsequenceProvenance,
    ResolvedConsequence, ConsequenceAggregationResult,
    request_fingerprint, aggregate_consequence_requests,
)
__all__ += [
    "AggregationMode", "ConsequencePolicy", "ConsequenceProvenance",
    "ResolvedConsequence", "ConsequenceAggregationResult",
    "request_fingerprint", "aggregate_consequence_requests",
]

from visual_engine.runtime.consequence_bindings import (
    StateConsequenceBinding, EffectConsequenceBinding, ConsequenceBindingSet,
    ConsequenceBindingResult, compile_resolved_consequences, apply_consequence_binding_result,
)
__all__ += [
    "StateConsequenceBinding", "EffectConsequenceBinding", "ConsequenceBindingSet",
    "ConsequenceBindingResult", "compile_resolved_consequences", "apply_consequence_binding_result",
]
from .appearance_contract import (AppearanceContribution, AppearanceDomain, AppearanceResolutionInput, AppearanceResolutionResult, DomainContract, DomainContractError, DomainFieldContract, DOMAIN_CONTRACTS, build_appearance_input, build_component_appearance_input, resolve_appearance_contract, validate_appearance_contribution, validate_appearance_contributions)
from .appearance_layers import (
    LayerActivationMode, LayerConflictMode, AppearanceLayerBinding,
    AppearanceLayerPolicy, AppearanceLayerProvenance, AppearanceLayerDecision,
    AppearanceLayerResolution, resolve_appearance_layers,
)
__all__ += [
    "LayerActivationMode", "LayerConflictMode", "AppearanceLayerBinding",
    "AppearanceLayerPolicy", "AppearanceLayerProvenance", "AppearanceLayerDecision",
    "AppearanceLayerResolution", "resolve_appearance_layers",
]
from .domain_resolution import (
    DomainResolutionStatus, DomainDependency, DomainResolvedField,
    DomainResolutionProvenance, DomainResolutionInput, DomainResolutionResult,
    validate_domain_resolution_result, unresolved_domain_result,
)
from .domain_input_factory import build_domain_resolution_input
__all__ += [
    "DomainResolutionStatus", "DomainDependency", "DomainResolvedField",
    "DomainResolutionProvenance", "DomainResolutionInput", "DomainResolutionResult",
    "build_domain_resolution_input", "validate_domain_resolution_result",
    "unresolved_domain_result",
]
from .base_resolution import (
    BASE_RESOLVER_ID, BASE_RESOLVER_VERSION, BaseResolutionError,
    build_base_resolution_input, build_base_resolution_input_from_role,
    build_base_resolution_input_from_typed, resolve_base_domain, resolve_base_domain_from_typed,
)
__all__ += [
    "BASE_RESOLVER_ID", "BASE_RESOLVER_VERSION", "BaseResolutionError",
    "build_base_resolution_input", "build_base_resolution_input_from_role",
    "build_base_resolution_input_from_typed", "resolve_base_domain", "resolve_base_domain_from_typed",
]

from .material_resolution import (
    MATERIAL_RESOLVER_ID, MATERIAL_RESOLVER_VERSION, MaterialResolutionError,
    build_material_resolution_input, resolve_material_domain,
)
__all__ += [
    "MATERIAL_RESOLVER_ID", "MATERIAL_RESOLVER_VERSION", "MaterialResolutionError",
    "build_material_resolution_input", "resolve_material_domain",
]

from .color_spaces import (
    ColorSpace, ColorSpaceError, ColorRGBA, parse_hex_color, canonicalize_hex_color,
    srgb_channel_to_linear, linear_channel_to_srgb,
)
__all__ += [
    "ColorSpace", "ColorSpaceError", "ColorRGBA", "parse_hex_color",
    "canonicalize_hex_color", "srgb_channel_to_linear", "linear_channel_to_srgb",
]

from .base_color_resolution import (
    BASE_COLOR_RESOLUTION_VERSION, BaseColorInvalidation, BaseColorResolution,
    adapt_legacy_base_color, base_color_invalidation, base_color_resolution_fingerprint,
    resolve_base_color,
)
__all__ += [
    "BASE_COLOR_RESOLUTION_VERSION", "BaseColorInvalidation", "BaseColorResolution",
    "adapt_legacy_base_color", "base_color_invalidation", "base_color_resolution_fingerprint",
    "resolve_base_color",
]
from .palette_resolution import (
    PALETTE_RESOLUTION_VERSION, PaletteResolution, palette_resolution_fingerprint,
    palette_invalidation, resolve_palette,
)
__all__ += [
    "PALETTE_RESOLUTION_VERSION", "PaletteResolution", "palette_resolution_fingerprint",
    "palette_invalidation", "resolve_palette",
]
from .appearance_composition import (
    APPEARANCE_COMPOSITION_VERSION, AppearanceCompositionError,
    AppearanceCompositionRequest, AppearanceCompositionProvenance,
    AppearanceComposition, CompositionMode, CompositionSource,
    appearance_composition_fingerprint, resolve_appearance_composition,
)
__all__ += [
    "APPEARANCE_COMPOSITION_VERSION", "AppearanceCompositionError",
    "AppearanceCompositionRequest", "AppearanceCompositionProvenance",
    "AppearanceComposition", "CompositionMode", "CompositionSource",
    "appearance_composition_fingerprint", "resolve_appearance_composition",
]

from .appearance_role_bridge import (
    ROLE_BRIDGE_VERSION, AppearanceRoleBridgeError, RoleContributionSource,
    AppearanceRoleContribution, bridge_appearance_composition, bridge_fingerprint,
    bridge_to_appearance_input, role_bridge_invalidation,
)
__all__ += [
    "ROLE_BRIDGE_VERSION", "AppearanceRoleBridgeError", "RoleContributionSource",
    "AppearanceRoleContribution", "bridge_appearance_composition", "bridge_fingerprint",
    "bridge_to_appearance_input", "role_bridge_invalidation",
]

from .typed_appearance_input import (
    TYPED_APPEARANCE_INPUT_VERSION, TypedAppearanceInputError, TypedAppearanceInput,
)
__all__ += ["TYPED_APPEARANCE_INPUT_VERSION", "TypedAppearanceInputError", "TypedAppearanceInput"]

from .color_resolution import (
    COLOR_RESOLVER_ID, COLOR_RESOLVER_VERSION, COLOR_DOMAIN_INPUT_VERSION,
    ColorResolutionError, TypedColorInput, build_color_resolution_input_from_typed,
    resolve_color_domain, resolve_color_domain_from_typed, color_domain_fingerprint,
    color_domain_invalidation,
)
__all__ += [
    "COLOR_RESOLVER_ID", "COLOR_RESOLVER_VERSION", "COLOR_DOMAIN_INPUT_VERSION",
    "ColorResolutionError", "TypedColorInput", "build_color_resolution_input_from_typed",
    "resolve_color_domain", "resolve_color_domain_from_typed", "color_domain_fingerprint",
    "color_domain_invalidation",
]

from .production_face_overlap_visibility import resolve_face_overlap_visibility
from .production_face_overlap_relations import resolve_production_face_overlap_relations
from .production_owner_geometry import extract_production_owner_geometry
from .production_visual_styles import resolve_production_visual_styles
from .production_render_result import ProductionRenderResult
from .production_render_session import ProductionRenderSession
from .production_face_overlap_visibility import ProductionVisibilityResolution
from .production_pair_occlusion import ProductionPairOcclusion, resolve_production_pair_occlusion
from .production_hair_ear_occlusion import ProductionHairEarOcclusion, resolve_hair_ear_occlusion
from .production_hair_ear_relations import resolve_production_hair_ear_relations
from .production_head_ear_occlusion import ProductionHeadEarOcclusion, resolve_head_ear_occlusion
from .production_head_ear_relations import resolve_production_head_ear_relations
__all__ += [
    "ProductionRenderResult", "ProductionRenderSession", "ProductionVisibilityResolution", "resolve_face_overlap_visibility", "resolve_production_face_overlap_relations", "extract_production_owner_geometry", "resolve_production_visual_styles",
    "ProductionPairOcclusion", "resolve_production_pair_occlusion",
    "ProductionHairEarOcclusion", "resolve_hair_ear_occlusion", "resolve_production_hair_ear_relations",
    "ProductionHeadEarOcclusion", "resolve_head_ear_occlusion", "resolve_production_head_ear_relations",
]
