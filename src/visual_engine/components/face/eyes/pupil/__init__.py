"""Pupil value specifications and pupil-specific optical effects."""  # CMP-EYE-PUPIL: package boundary is explicit.
from .effects import PupilGlowSpec, PupilSmokeSpec  # PUPIL-API: expose pupil effect specifications.
from .spec import PupilSpec  # PUPIL-API: expose the canonical pupil specification.
