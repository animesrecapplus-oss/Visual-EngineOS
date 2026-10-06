# Pre-change impact audit — CMP-FACE-VIS-001

Fresh V1.77 visual sampling found real defects in the existing production default: the hair lower contour read as a cap, the nose bridge rose too high, the nose/mouth clearance was too small, and ear Y placement was offset by `0.02` from eye centers.

The audit also demonstrated that existing components already expose real variation controls for eye shape/detail, hair dimensions/detail density, face shape and authored visual color. The correction therefore uses existing consumers rather than inventing a new renderer abstraction.

Persistence/database: no affected consumer found.
Cache/fingerprint: hair generator version incremented because geometry changed.
Visual behavior: intentionally changed only for the reported default face calibration and its hair detail controls.
