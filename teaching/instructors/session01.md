# Session 1 — Instructor preparation

The source for the student practical is `docs/modules/ROOT/pages/labs/session01-digital-twins.adoc`.
It is both an executable Antora page and the source of the exported notebook.
Do not edit the generated notebook separately.

Run with the course environment active:

```sh
npm run antora
python scripts/verify-session01.py
python scripts/package-course.py
```

The verification writes an executed notebook, an instructor notebook with independent numerical checks, and an HTML fallback to `build/course-release/`. These are outside the published Antora components.
The package command creates `build/course-release/course-rom-session01-20260910.zip` with the website and student material; the instructor reference notebook is excluded.

The supplied model and all observations are synthetic. At the opening, students identify the model, state, parameter, output and observation operator. They change the trial parameter and examine the mean and maximum. Increasing diffusion lowers the profile for this fixed source and zero boundary data. The mean is the integral on the unit interval, not the arithmetic mean of interior nodal values.

The default trial parameter is 1.0 and the synthetic reference parameter is 0.35. Setting noise to zero therefore does not remove the discrepancy. Setting the trial parameter to the reference removes the model discrepancy in this controlled setup, but noisy observations still differ from the noiseless prediction. This diagnostic is not an inverse algorithm: the synthetic reference parameter is deliberately revealed for evaluation.

Sensor locations are mapped to grid points and their actual positions are printed. Distinct requested positions can map to the same grid point; the starter raises a clear error in that case. If students change the trial parameter, remind them to rerun its solve before the observation comparison.

Discussion should distinguish numerical error, parameter/model discrepancy and observation noise. Five observations do not determine an arbitrary 64-dimensional state. Reduced spaces and assumptions will make subsequent reconstruction possible. A small equation residual does not establish physical fidelity.

No assimilation algorithm is assigned in this first experiment. End by locating the forthcoming GEIM/PBDW and KF/EnKF work in the model–observation loop, and emphasize that assimilation is a required course outcome.

Allow about 10 minutes for framing/access and 30 minutes for notebook work. If students struggle with setup, pair them with a working environment and retain the error details for follow-up. Use the executed page or HTML as a reference while preserving student experimentation.
