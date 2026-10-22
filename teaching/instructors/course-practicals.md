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

The thermal-fin notebook now has two stages at the same URL: prediction/POD-greedy after stationary greedy, and an EnKF continuation later. Part A follows the opening of the original parabolic PDF: Bi in [0.01, 1], T=10, dt=0.1, zero initial state and discrete impulse training. The compact coarse mesh replaces the PDF's medium mesh for classroom speed. The original output is the integral M@ones (divide by area only when explicitly requesting a mean). Validation uses Bi=0.05 and 1-cos(t). Six modes give about 2% peak-normalized output discrepancy with 1333 full unknowns versus six coefficients. Full/reduced fields share a color scale; signed field error and full output histories are displayed. The long original problem set is reading, not an assignment for this session.

The stationary greedy TP reuses the earlier two-parameter 1D bar and G=K+M. Recorded scan-selected sequences make the plots runnable while the student adaptive loops remain TODOs. Instructor-only loops in the check scripts reproduce those sequences, validate certificates and rescan at the final rank. Parameter selection must not use diagnostic reference solves. Only stationary SPD energy errors and nested trajectory projection errors carry the stated monotonicity claims.

The later EnKF continuation uses Bi=0.12 for the forecast and Bi=0.05 for observations, under the validation control. Reduction, parameter mismatch and assimilation are reported separately. These experiment diagnostics are not general performance guarantees; do not hardcode machine-dependent timings as speedups.

Session 14 is a separate assimilation benchmark using the same matrix data and filter structure; it retains its four-parameter training ensemble and sinusoidal input, rather than claiming to reproduce the new part-A experiment unchanged. Require students to freeze a configuration before creating the separate Bi=0.085, seed=150 experiment. The instructor checks execute that extra checkpoint, but do not reveal its results in the student notebook. The nondimensional mean-temperature threshold 0.20 is a discussion scenario, not a safety criterion.

## References and source adaptation

The public notes link scholarly references and published teaching data. They never require students to open private TeX or local root notebooks.

Internal source selection: the reduction/greedy sources inform session 4; `rb-non-affine.tex` and the moving-source EIM/DEIM notebooks inform sessions 5–7; its GEIM/PBDW sections and `rb-da.tex` inform sessions 8–10; `kf_enkf.tex` and the historical filtering practicals inform sessions 11–12. The thermal-fin prediction section adapts the opening of the original parabolic problem-set PDF (published as problem-set-parabolic.pdf), using the original assembled finite-element matrices. The long problem set is deliberately not assigned in full.

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
