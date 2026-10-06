"""Upper/lower lash domains and lash-specific optical effects."""  # CMP-EYE-LASHES: sibling ownership boundary.
from .effects import LashShadowSpec  # LASH-API: lash shadow now has one canonical owner.
from .spec import LashSpec, LowerLashSpec  # LASH-API: expose lash morphology specifications.
