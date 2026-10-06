# Legacy line-budget debt register — V1.52

## Rule

The 150-line budget is now mandatory for new/modified files. Existing oversized files are explicit legacy nonconformities. They may not receive unrelated feature growth; each can be touched only through a responsibility-driven extraction brick.

## Current inventory

| Lines | Module |
|---:|---|
| 401 | `visual_engine.runtime.appearance_contract` |
| 398 | `visual_engine.runtime.contract` |
| 187 | `visual_engine.runtime.domain_resolution` |
| 372 | `visual_engine.components.face.generators` |
| 347 | `visual_engine.persistence.serialization` |
| 345 | `visual_engine.runtime.color_spaces` |
| 332 | `visual_engine.runtime.spatial_relationships` |
| 312 | `visual_engine.runtime.appearance_layers` |
| 302 | `visual_engine.components.common.base_color` |
| 292 | `visual_engine.persistence.postgres` |
| 291 | `visual_engine.runtime.visibility` |
| 281 | `visual_engine.components.common.visual_contract` |
| 276 | `visual_engine.components.common.palette` |
| 271 | `visual_engine.runtime.visibility_attribution` |
| 248 | `visual_engine.runtime` |
| 248 | `visual_engine.runtime.base_color_resolution` |
| 246 | `visual_engine.runtime.geometry_fingerprint` |
| 245 | `visual_engine.components.face.eyes.generator` |
| 243 | `visual_engine.components.face.eyes.geometry.spherical_assembly` |
| 243 | `visual_engine.components.face.eyes.morphology.canthus_metrics` |
| 242 | `visual_engine.components.face.eyes.geometry.builder` |
| 241 | `visual_engine.components.face.eyes.reference.v120_review` |
| 239 | `visual_engine.runtime.consequences` |
| 238 | `visual_engine.runtime.base_resolution` |
| 236 | `visual_engine.render.geometry_svg` |
| 233 | `visual_engine.render.eye_svg_effects` |
| 232 | `visual_engine.runtime.dependencies` |
| 230 | `visual_engine.components.face.eyes.reference.digitization` |
| 230 | `visual_engine.runtime.appearance_role_bridge` |
| 226 | `visual_engine.runtime.color_resolution` |
| 224 | `visual_engine.render.eye_svg_primitives` |
| 220 | `visual_engine.components.face.eyes.morphology.envelope` |
| 220 | `visual_engine.components.face.eyes.pair` |
| 219 | `visual_engine.components.face.eyes.reference.calibration` |
| 211 | `visual_engine.runtime.graph` |
| 211 | `visual_engine.runtime.region_maps` |
| 210 | `visual_engine.runtime.appearance_composition` |
| 209 | `visual_engine.components.face.eyes.geometry.continuity` |
| 209 | `visual_engine.runtime.geometry_cache` |
| 209 | `visual_engine.runtime.resolution_cache` |
| 207 | `visual_engine.runtime.effects` |
| 201 | `visual_engine.components.face.eyes.reference.acquisition` |
| 193 | `visual_engine.components.face.eyes.reference.v122_sample_gate` |
| 191 | `visual_engine.runtime.consequence_bindings` |
| 188 | `visual_engine.render.eye_svg_contours` |
| 186 | `visual_engine.components.face.eyes.geometry.depth_occlusion` |
| 183 | `visual_engine.runtime.versioning` |
| 182 | `visual_engine.components.face.eyes.reference.pixel_trace` |
| 182 | `visual_engine.runtime.typed_appearance_input` |
| 180 | `visual_engine.components.face.eyes.reference.v121_trace_capture` |
| 177 | `visual_engine.runtime.placement_visibility` |
| 176 | `visual_engine.runtime.consequence_aggregation` |
| 173 | `visual_engine.components.common.geometry_contract` |
| 173 | `visual_engine.runtime.geometry_contract_transform` |
| 169 | `visual_engine.runtime.material_resolution` |
| 167 | `visual_engine.runtime.coverage` |
| 163 | `visual_engine.runtime.state_policy` |
| 162 | `visual_engine.components.face.eyes.geometry.contour` |
| 161 | `visual_engine.runtime.geometry_transform` |
| 159 | `visual_engine.components.face.eyes.gaze.solver` |
| 159 | `visual_engine.components.face.eyes.morphology.spec` |
| 157 | `visual_engine.components.face.eyes.reference.review` |
| 157 | `visual_engine.runtime.effect_color` |
| 154 | `visual_engine.components.face.eyes.reference.v120_compare` |
| 153 | `visual_engine.runtime.palette_resolution` |

## Governance meaning

The inventory is debt, not permission to split 68 files at once. Each future brick selects one real module and one responsibility, proves consumers and impact, then extracts one owner.
A module drops from this register only after source freeze, tests, regression, benchmark and documentation are certified.
