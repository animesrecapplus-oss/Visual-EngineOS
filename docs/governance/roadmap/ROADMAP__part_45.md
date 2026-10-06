# Roadmap — V1.91

## V1.91 completion

- [x] reopen exact V1.89 checkpoint;
- [x] incorporate V1.90 audit findings without promoting audit-only code;
- [x] reproduce HumanFace bilateral-side defect;
- [x] verify canonical EyePair side semantics;
- [x] select one bounded owner and reject coordinate inference;
- [x] remove unused duplicate HumanFace eye-input helper;
- [x] correct Eye default side propagation;
- [x] bump geometry generator version;
- [x] add hostile/negative-space/production tests;
- [x] validate cache identity;
- [x] produce and inspect normal/boundary/interaction visual evidence;
- [x] measure the changed input boundary;
- [x] update micro-component truth dossier and exact line ranges.

## Certification limitation

The monolithic current test suite was attempted but exceeded the execution wall-clock limit. Affected ocular/production suites and the complete `tests/components` + `tests/integration` trees passed. No complete-current-suite PASS claim is made.

## Next frontier

The next brick is the separately owned **generic ocular aperture/depth/mask integration audit/implementation**. It must begin with a fresh horizontal VERIFY/IMPACT pass and must prove its canonical owner and real production consumer before runtime modification.

Do not combine it with prompt compilation, default-camera semantics, COLOR expansion or generic component-side architecture.
