# Internal source provenance and editorial corrections

These notes support maintenance; they are outside Antora's published modules. Students receive complete course pages, selected notebook exports, public PDF companions and accessible scholarly references. Private source filenames are not assigned reading.

Paths below refer to the external `rbm` teaching collection unless explicitly labeled course-rom. Source hashes and dependency details remain in `materials/catalog/sources.json`.

| Published unit | Internal source | Adaptation and review notes |
|---|---|---|
| `rom::digital-twins.adoc` | `Slides/rbm/course-rom-outline.tex`; course-rom's local `rbm_tiny_lab.ipynb` | Digital-twin, inference-cycle and model/data themes; new worked introduction and synthetic-observation activity. The public 2024 introductory PDF is a companion, not a complete source conversion. |
| `rom::notation.adoc` | Inner-products/norms, RB formulation, residual-estimation and Kalman-filtering sections | Shared conventions authored for the new notes rather than a transcription of one slide deck. |
| `rom::reduction/galerkin.adoc` | `Slides/rbm/rbellipticlinear_galerkin.tex`, `Slides/rbm/course-rom-rbm-decomposition.tex` | Historical N/full-dimension symbols become r/n. Retain symmetry for energy optimality and distinguish the POD metric from the energy metric. |
| `rom::reduction/pod.adoc` | `Slides/rbm/course-rom-svd-pod.tex`, `Slides/rbm/course-rom-rbm-pod.tex` | Specify metric and snapshot weights before SVD; distinguish training projection optimality from held-out reduced-solve accuracy. Add the S1 PCA to S3 POD bridge and centered affine ROM. |
| `rom::certification/residual-bound.adoc` | `Slides/rbm/course-rom-rbm-error.tex` and `rbellipticlinear_error` fragments | The source slide omits the square root in the residual dual norm; the current notes use the correct expression. The discrete reaction–diffusion spectrum and QR-residual exercise are supplied for this course. |
| `course-rom::labs/session01-digital-twins.adoc` | course-rom's local `rbm_tiny_lab.ipynb` | Adapted finite-difference assembly and full-order solve; new parameter/output and synthetic-observation tasks. The maintained student export is generated from the AsciiDoc page and contains all necessary code/data. |

The historical POD citation was dated 2010 in the source slides. The student-facing citation now links to Volkwein's available 43-page notes, dated 7 December 2011 on their first page: https://www.math.uni-konstanz.de/numerik/personen/volkwein/teaching/POD-Vorlesung.pdf.

The 2024 thermal-fin assignment previously named unavailable `PS2_Python.zip`, `PS4_Python.zip` and `plotsolution.m`. The published `homework-2024-data.zip` actually contains `FE_grid.mat`, `FE_matrix.mat`, `FE_matrix_mass.mat` and `RB_sample.mat`, but no plotting helper. The assignment now links to that archive and directs students to its existing inline Python plotting function. This access correction does not claim that the entire historical assignment has undergone numerical revalidation.

## RB/POD restoration against the teaching supports — 17 September 2026

The earlier native pages were a selective summary, not a faithful replacement for all the explanatory steps in the slides. The following mapping records this restoration so future shortening does not silently remove prerequisites again.

| Reviewed source | Native section / treatment |
| --- | --- |
| Published `lecture-rbobm-beamer-approx.pdf`, pp. 4–7 | RB objectives, cost amortization and existing residual/effectivity chapter. |
| Same PDF, pp. 8–11 | `galerkin.adoc#solution-manifold`: solution family, linear approximability, original snapshot-family illustration plus a numerical geometric example. No claim that every smooth parameter image is a smooth embedded manifold or easy to approximate linearly. |
| Same PDF, pp. 12–14 | `#parameter-sampling`, `#hierarchical-spaces`, `#taylor-hermite`: equidistributed/log-random samples, curse of dimensionality, nested/non-nested Lagrangian spaces, supplementary sensitivity spaces. |
| Same PDF, pp. 15–16 | `#basis-matrix`, `#snapshot-orthogonalization`: full-basis coordinates of reduced functions, matrix dimensions, metric Gram–Schmidt and dependence handling. |
| Same PDF, pp. 17–22 | `#projection-steps`, `#state-projection`, `#compliant-output`, `#rb-conditioning`: algebraic derivations, distinction between testing/reconstruction/projection, compliant-output identity and bounds, conditioning proof. |
| Same PDF, pp. 24–41 | `#reference-domain`: common reference coordinates, pullback, Jacobian and gradient transformations, rectangular stretching example. Full vector/advection transformation treatment remains in the linked PDF; this is not recorded as a full chapter conversion. |
| Same PDF, pp. 42–51 | Original heat-transfer illustration and explanation of the piecewise map and its six affine operator terms. Physical PDE and full vector formulas remain in the public companion. |
| `Slides/rbm/course-rom-svd-pod.tex`, active SVD/POD sections | `pod.adoc#svd-foundations`, `#svd-low-rank`, `#pod-first-mode`: full/thin/compact/truncated SVD, geometry, modal coefficients, norm identities, best-rank argument and energy maximization. |
| Same source, correlation, weighted and continuous POD sections; `course-rom-rbm-pod.tex` | `#snapshot-correlation`, `#snapshot-pod-algorithm`, `#continuous-pod`: weighted correlation eigenproblem, mode reconstruction, numerical limitations, operator/adjoint, Hilbert–Schmidt tail and quadrature interpretation. |
| SVD noise-threshold/image-compression digression | A supplementary paragraph distinguishes denoising, energy truncation and compression. Specific statistical threshold formulas and historical image examples are not presented as ROM guarantees; they remain outside this course's required implementation. |

### Corrections preserved in the native notes

- The finite set of plotted snapshots is not a linear space until its span is taken. A reduced basis matrix is rectangular; the state projector is a different, square map.
- In the slide projection formulas, missing leading basis factors / transposes would make dimensions inconsistent; the native metric projector is `Z (Z^T G Z)^{-1} Z^T G`.
- The `m × m` snapshot-correlation approach is dimensionally attractive for `m << n`, not for `m >> n` as one summary slide says.
- Weighted mode reconstruction includes the snapshot square-root weights. The relative RMS criterion uses the square of the requested tolerance.
- A correlation operator is positive semidefinite, not necessarily positive definite. SVD transpose formulas retain the singular-value matrix; eigenvalue identities use `YY^T u_i = sigma_i^2 u_i` and `Y^T Y v_i = sigma_i^2 v_i`.
- PDF p. 35 must distinguish the inverse Jacobian matrix from the reciprocal determinant. The heat-transfer inverse map on p. 49 requires `(x_tilde + 2 mu_1)/(1 + 3 mu_1)`; the sign is checked by fixing the interface and mapping the right endpoint.
- Geometric mapping choices can affect finite-dimensional reduced-space approximation, not only the full-order mesh error.

### Figure provenance and reproduction

`materials/modules/ROOT/images/reduction/snapshot-family-slides.png` is an illustration-region extraction of PDF p. 11; `heat-transfer-domain-slides.png` is from p. 43. Both publicly caption the author, PDF and page. No private slide assets are needed for the build. Extraction coordinates, scale and page numbers are maintained in `scripts/render-reduction-figures.py`, which requires NumPy, Matplotlib and Poppler only when regenerating figures.

`solution-family.svg` and `svd-geometry.svg` are original mathematical illustrations generated by the same script. The first visualizes the explicitly stated family `(1,t,0.1t^2)`; the second visualizes a matrix with singular values 2 and 0.7. They do not reproduce measured convergence results from the source slides.

## Executable image compression in the POD chapter

The image-compression digression is now an executed example in `pod.adoc#image-compression`, rather than an excluded historical illustration. The public `lecture-rbobm-beamer-svd-pod.pdf`, pp. 18–19, supplies the Melencolia I magic-square example. `scripts/extract-pod-image.py` extracts the original panel of the embedded comparison image from PDF page 19, converts it to grayscale without resizing, and records the crop and hashes in `materials/modules/ROOT/attachments/data/melencolia-magic-square.json`. The resulting 550 × 569 raster is a slide reproduction, not the unavailable original matrix; ranks 1, 20 and 40 are retained but all errors, singular values and storage fractions are recomputed. Student notes disclose this distinction.

Four dynamic cells load the local image, compute the SVD, generate two figures, select a rank by relative error and verify the Frobenius tail identity. Display clipping is excluded from the numerical errors. Storage counts distinguish three factors, two factors with absorbed singular values, raw uint8 pixels and PNG encoding. A fifth code cell is the existing weighted-correlation example. The exported full chapter uses public web links for Antora cross-references and figures; the image file is supplied separately. `scripts/verify-pod-notebook.py` executes all five exported cells in a temporary folder containing only that image, using the invoking Python environment, and saves an executed inspection copy outside the source tree.
