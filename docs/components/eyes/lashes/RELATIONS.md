# CMP-EYE-LASH — relations

## REL-LASH-PERIOCULAR

Lashes belong to the `ORBIT / PERIOCULAR` branch. They are not children of sclera or pupil.

## REL-LASH-EYELID

Lash placement follows the resolved eyelid geometry at render time, but the eyelid system is not the lash spec's
parent/owner.

## REL-LASH-TERMINAL

Canthus terminal exclusion is a renderer/geometry behavior documented in earlier ocular contracts. V1.85 does not
move that ownership into `lashes/spec.py`.

## REL-LASH-SHADOW

`LashShadowSpec` is canonically owned by `lashes/effects.py`; V1.85 does not alter that ownership.

## REL-LASH-VISIBILITY

Visibility/covered/closed suppression remains downstream in the render path.

## REL-LASH-API

Legacy exports through `definitions.py` and `geometry/__init__.py` remain compatibility paths, not duplicate owners.
