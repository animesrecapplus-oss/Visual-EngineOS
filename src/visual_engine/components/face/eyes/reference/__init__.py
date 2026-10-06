"""Reference digitization and authoritative ocular transform-resolution contracts."""

from .digitization import (
    ReferenceCurve, ReferenceFamily, ReferenceSample, ReferenceSource,
    ReferenceDigitizationSet, load_reference_dataset, validate_reference_dataset, measure_reference_sample,
)
from .dataset import load_v18_reference_envelope_dataset
from .transform import OcularTransformResolution, resolve_ocular_geometry, resolve_ocular_transform
from .acquisition import ReferenceAcquisitionRecord, sha256_file, inspect_image_file, inspect_image_metadata, verify_reference_file, acquire_reference_file, preserve_reference_file, segment_reference_sheet, write_acquisition_manifest
from .trace import curve_metrics, endpoint_metrics, measure_reference_sample_v19

__all__ = [
    "ReferenceCurve", "ReferenceFamily", "ReferenceSample", "ReferenceSource",
    "ReferenceDigitizationSet", "load_reference_dataset", "validate_reference_dataset", "measure_reference_sample",
    "load_v18_reference_envelope_dataset", "OcularTransformResolution",
    "resolve_ocular_geometry", "resolve_ocular_transform",
    "ReferenceAcquisitionRecord", "sha256_file", "inspect_image_file", "verify_reference_file",
    "acquire_reference_file", "preserve_reference_file", "segment_reference_sheet", "write_acquisition_manifest", "inspect_image_metadata",
    "curve_metrics", "endpoint_metrics", "measure_reference_sample_v19", "TraceRegion", "trace_component_candidates", "digitize_approved_eye", "ReferenceEngineAlignment", "polyline_error", "overlay_metrics", "render_reference_engine_overlay",
    "CandidateReview", "ReviewManifest", "ReviewerStatus", "review_from_segmentation", "apply_review_decision", "save_review_manifest", "load_review_manifest", "render_review_board",
    "TerminalResolution", "resolve_terminals", "canthus_pixel_metrics", "caruncle_metrics", "epicanthus_status", "sample_calibration_record", "mor_ranges", "FollowStrengthFit", "fit_eyelid_surface_follow_strength", "promote_eyelid_surface_follow_strength",
    "MANUAL_UPPER_TRACE_ID", "MANUAL_LOWER_TRACE_ID",
    "TraceRegionV121", "ManualPolylineV121", "V121TraceCapture", "trace_capture_to_json", "load_trace_capture", "digitize_v121_capture", "inspect_trace_components",
    "V122DigitizedSample", "V122SampleQualification", "V122DualSampleGate", "digitize_v122_sample", "qualify_sample", "build_dual_sample_gate", "gate_to_json",
]

from .pixel_trace import TraceRegion, trace_component_candidates, digitize_approved_eye
from .overlay import ReferenceEngineAlignment, polyline_error, overlay_metrics, render_reference_engine_overlay

from .review import CandidateReview, ReviewManifest, ReviewerStatus, review_from_segmentation, apply_review_decision, save_review_manifest, load_review_manifest, render_review_board
from .calibration import (TerminalResolution, resolve_terminals, canthus_pixel_metrics, caruncle_metrics, epicanthus_status, sample_calibration_record, mor_ranges, FollowStrengthFit, fit_eyelid_surface_follow_strength, promote_eyelid_surface_follow_strength)

from .v120 import (
    EyeIdentification, CaruncleReview, EpicanthusReview, TraceRegionV120, V120CandidateReview,
    MANUAL_UPPER_TRACE_ID, MANUAL_LOWER_TRACE_ID,
    create_pending_v120_manifest, load_v120_reviews, approved_v120_records, digitize_v120_review,
    build_fixed_reference_engine_alignment, evaluate_follow_strength_sample,
    aggregate_follow_strength_results, select_candidate_strength,
)

from .v121_trace_capture import (
    TraceRegionV121, ManualPolylineV121, V121TraceCapture,
    trace_capture_to_json, load_trace_capture, digitize_v121_capture, inspect_trace_components,
)

from .v122_sample_gate import V122DigitizedSample, V122SampleQualification, V122DualSampleGate, digitize_v122_sample, qualify_sample, build_dual_sample_gate, gate_to_json
