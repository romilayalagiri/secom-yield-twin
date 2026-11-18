# Decision Log

Write down every choice about data or methods, with the reason.
This becomes the backbone of the methodology chapter.

| Date | Week | Decision | Reason | Effect / evidence |
|------|------|----------|--------|-------------------|
| | 1 | Project structure created with help from Claude (AI) | Faster setup; declared under AI policy | Reviewed and tested by me |
| 17-11-2026 | 1 | SECOM licence: CC BY 4.0 (sharing and adaptation allowed with credit) | Checked on UCI page | Cited in thesis |
| | 1 | Labels recoded: -1 → 0 (pass), 1 → 1 (fail) | Standard 0/1 coding for models | Original kept as `label_raw` |
| | | | | |
| 17-11-2026 | 1 | Data loaded and validated | 1,567 runs, 590 sensors, 104 failures (6.6%), 19.07.2008–17.10.2008, 4.5% missing | All checks passed |
| 18-11-2026 | 8 | Finding: 116 of 590 sensors are constant | Profiling (src/profiling.py) | Rule: remove constant sensors (fitted on training data only) |
| 18-11-2026 | 8 | Finding: 28 sensors have over 50% missing; 4 sensors 91.2%, 4 sensors 85.6% | Missing values come in groups, likely shared machines/steps | Rule and threshold to agree with supervisor at M2 |
| 18-11-2026 | 8 | Finding: 538 sensors have 0-5% missing | Most sensors nearly complete | Small gaps to be imputed inside training folds |
| 18-11-2026 | 8 | Finding: 178 of 446 usable sensors are near-duplicates (103 groups, abs. correlation >= 0.95) | src/redundancy.py | Rule: keep 1 sensor per group, decided on training data only; threshold 0.95 to test for sensitivity |
| 18-11-2026 | 8 | Funnel: 590 -> 446 (remove constant + over 50% missing) -> 268 (remove duplicates) | Exploration on full data | To be reported at M2 |
| 18-11-2026 | 8 | Observation: duplicate sensors repeat about every 135-138 columns | Suggests repeated measurement blocks | Cannot be confirmed (anonymised data); mention carefully |