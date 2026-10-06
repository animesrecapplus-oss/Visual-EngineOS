# Impact map

V1.59 source change: `production_hair_ear_occlusion.py:1-77` now delegates to `production_pair_occlusion.py:53-107`.
Output contract, Hair/Ear attribution and production result remain unchanged.
No database, COLOR, cache-lifetime or renderer policy change.

V1.63 orchestration extraction: the leaf owner is now called by `runtime/production_hair_ear_relations.py`; its one-pair contract is unchanged.
