# Component truth — CMP-FACE-NOSE-001

Identity: one direct `Nose` child of `HumanFace`.
Owner: `src/visual_engine/components/face/generators.py:231-306`.
Parent: `HumanFace` authored in `src/visual_engine/entities/face.py:4-51`.

Responsibility: generate the existing finite stylized Nose geometry, including the main closed path and two shallow nostril detail paths.
Non-responsibility: full nasal anatomy, face placement policy, renderer, COLOR, cache lifetime, persistence schema, deformation and material simulation.

Real production consumer: the face-with-eyes-nose composite and later mouth/ear/hair production composites through the registered generator.
