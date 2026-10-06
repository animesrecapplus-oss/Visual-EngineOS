"""V1.20 public compatibility facade.

Implementation is split into review and comparison modules to keep each module
small enough for precise audit and maintenance.
"""

from .v120_review import (
    EyeIdentification, CaruncleReview, EpicanthusReview, TraceRegionV120,
    V120CandidateReview, MANUAL_UPPER_TRACE_ID, MANUAL_LOWER_TRACE_ID,
    create_pending_v120_manifest, load_v120_reviews,
    approved_v120_records, digitize_v120_review,
)
from .v120_compare import (
    build_fixed_reference_engine_alignment, evaluate_follow_strength_sample,
    aggregate_follow_strength_results, select_candidate_strength,
)

__all__ = [
    "EyeIdentification", "CaruncleReview", "EpicanthusReview", "TraceRegionV120",
    "MANUAL_UPPER_TRACE_ID", "MANUAL_LOWER_TRACE_ID",
    "V120CandidateReview", "create_pending_v120_manifest", "load_v120_reviews",
    "approved_v120_records", "digitize_v120_review",
    "build_fixed_reference_engine_alignment", "evaluate_follow_strength_sample",
    "aggregate_follow_strength_results", "select_candidate_strength",
]
