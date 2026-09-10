# Teaching the complete 14-session route

Each session is a two-hour cours intégré, with roughly one hour of practical work inside that budget. The new sessions 4–14 each have a self-contained runnable baseline, timed tasks and a checkpoint. Do not assign all optional extensions in class. Homework pages group related sessions and suggest outside-class effort; dates and grading remain the instructor's decision.

## Unit preparation and expected diagnostics

| Sessions | Main evidence | Interpretation to draw out |
| --- | --- | --- |
| 4 | Greedy parameters, equal-rank held-out errors, valid certificates | The finite training stopping guarantee differs from POD's empirical average projection optimum. |
| 5–7 | Interpolation identities, DEIM bound, sampled source counts and repeated scalar-query timings | Source interpolation, reduced PDE error and actual online work must be separated. EIM rank 8 deliberately leaves visible error on narrow held-out sources. |
| 8–10 | Normalized averages, Riesz identity, PBDW beta, orthogonality and validation/test noise study | Exact observation fitting cannot identify invisible discrepancy; sensor scaling and regularization change the problem. |
| 11–12 | Analytic KF check, PSD covariance, stochastic EnKF covariance check, ensemble/noise comparisons | Finite-ensemble variability prevents a universal monotonic accuracy claim. Marginal intervals differ from simultaneous or calibrated nonlinear coverage. |
| 13–14 | Mass POD, imperfect full/reduced forecast comparison, reduced EnKF, rank/sensor comparison and untouched test | Reduction, parameter mismatch, observation noise and coefficient-space uncertainty have different meanings. |

The nominal thermal-fin run uses four training Biot numbers, a held-out truth at 0.07 and an imperfect forecast at 0.12. Six POD modes give approximately 0.004 mass RMSE relative to the imperfect full forecast; both forecast-only paths have approximately 0.316 error relative to truth. With the stated noise and seed, reduced EnKF gives about 0.080. These are default experiment diagnostics, not general performance guarantees. Timing values are machine-dependent and must not be hardcoded as speedups.

Session 14 reuses the preceding implementation. Require students to freeze a configuration before creating the separate Bi=0.085, seed=150 experiment. The instructor checks execute that extra checkpoint, but do not reveal its results in the student notebook. The nondimensional mean-temperature threshold 0.20 is a discussion scenario, not a safety criterion.

## References and source adaptation

The public notes link scholarly references and published teaching data. They never require students to open private TeX or local root notebooks.

Internal source selection: the reduction/greedy sources inform session 4; `rb-non-affine.tex` and the moving-source EIM/DEIM notebooks inform sessions 5–7; its GEIM/PBDW sections and `rb-da.tex` inform sessions 8–10; `kf_enkf.tex` and the historical filtering practicals inform sessions 11–12. The transient thermal-fin prediction/assimilation checkpoint is newly authored using the published 2024 finite-element matrices.

Do not relabel the local conductivity least-squares notebook as GEIM. The new GEIM practical actually selects residual/sensor pairs. The new PBDW implementation uses `Q = G^-1 H.T` and computes beta using whitened orthonormal bases; it does not carry forward the inconsistent quadrature scaling from older notebook variants.

The compact thermal data are produced by `scripts/prepare-thermal-fin.py` from the tracked public MATLAB ZIP. Its JSON records source and output hashes. No external corpus access is needed to build or execute the course.

## Release checks

Activate the course Python environment, then run:

```sh
npm run validate
npm run verify:labs
python3 scripts/package-course.py
```

The additional checker executes official notebook exports in fresh kernels, appends the independent mathematical checks from `teaching/instructors/checks/`, and writes reference notebooks only under ignored `build/course-release/`. Student previews contain only original student cells. The package refuses stale notebook, preview, requirements or data hashes. No instructor check cells enter Antora or student downloads.

Use `COURSE_PYTHON=/does/not/exist npm run site:static` and `python3 scripts/verify-course-site.py --static` to check the preview without Python execution. This does not replace the executable release checks.

No classroom completion, student workload feedback or public deployment is implied by local validation. Rehearse the upcoming two sessions, adjust optional tasks from actual student progress, and verify the deployed URLs after the instructor commits and publishes.


## Notebook reading links

The pinned exporter treats ordinary AsciiDoc page targets as notebook targets and does not resolve cross-component references. Until [upstream issue 7](https://github.com/feelpp/feelpp-antora-extensions/issues/7) is addressed, the new practicals use backend conditionals: normal Antora xrefs for the website, absolute published page/data links for downloaded notebooks. Export tests and the site audit cover these links. Students using the local backup can follow its website; absolute reading links in a notebook require the published site.


Wide dynamic Matplotlib figures also need the supplemental `course.css` rule in UI v0.53. It preserves the complete figure while fitting it to the article column. This is tracked in [UI issue 105](https://github.com/feelpp/antora-ui/issues/105); the course does not wait for an upstream release.
