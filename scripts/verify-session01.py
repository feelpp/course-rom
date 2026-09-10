"""Execute the exported student notebook and check independent numerical properties.

Run using the course virtual environment. Outputs are local instructor artifacts,
outside the Antora content roots; no solutions are added to student downloads.
"""
from pathlib import Path
import json
import sys

import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter

root = Path(__file__).resolve().parents[1]
source = root / "public/course-rom/_attachments/labs/session01-digital-twins.ipynb"
destination = root / "build/course-release"
destination.mkdir(parents=True, exist_ok=True)
notebook = nbformat.read(source, as_version=4)
nbformat.validate(notebook)
student_cell_count = len(notebook.cells)
notebook.cells.append(nbformat.v4.new_code_cell(r'''
# Instructor verification: compare the discrete solver with an analytic solution.
errors = []
for size in (31, 63, 127):
    xx, hh, KK, II, ff = assemble_system(size)
    mu = 0.35
    uu = solve_full(mu, KK, II, ff)
    exact = 1 - np.cosh((xx - 0.5) / np.sqrt(mu)) / np.cosh(0.5 / np.sqrt(mu))
    errors.append(float(np.max(np.abs(uu - exact))))
    assert np.linalg.norm((mu * KK + II) @ uu - ff, ord=np.inf) < 1e-10
ratios = np.array(errors[:-1]) / errors[1:]
assert np.all((ratios > 3.9) & (ratios < 4.1)), ratios

# Positive states, monotonic parameter response and the integral convention.
means = [mean_output(solve_full(mu, K, I, f), h) for mu in (0.1, 0.5, 2, 10)]
assert np.all(np.diff(means) < 0)
assert np.all(u_reference > 0)
assert np.isclose(mean_output(u_trial, h), np.trapezoid(np.r_[0, u_trial, 0], x_plot))
assert np.array_equal(H @ u_reference, u_reference[sensor_indices])

# Distinguish parameter mismatch from measurement noise in the opening task.
mismatch = np.sqrt(np.mean((H @ u_reference - H @ u_trial)**2))
assert mismatch > 0.05, mismatch
assert np.array_equal(H @ u_reference - H @ u_reference, np.zeros(len(sensor_indices)))
expected_noise = noise_std * np.random.default_rng(20260910).standard_normal(len(sensor_indices))
assert np.allclose(y - H @ u_reference, expected_noise)
assert sensor_rmse > 0
print("Independent checks passed: second-order convergence, residual, output, sensors and noise.")
print("Convergence ratios:", ratios)
print("Mean outputs:", means)
print("Noiseless mismatch:", mismatch)
'''))
NotebookClient(notebook, timeout=90, kernel_name="python3", resources={
    "metadata": {"path": str(destination)},
}).execute()
nbformat.write(notebook, destination / "session01-reference.ipynb")

student_run = nbformat.from_dict(notebook)
student_run.cells = student_run.cells[:student_cell_count]
nbformat.write(student_run, destination / "session01-executed.ipynb")
html, _ = HTMLExporter(template_name="classic").from_notebook_node(student_run)
(destination / "session01-starter.html").write_text(html)
figures = sum("image/png" in output.get("data", {})
              for cell in student_run.cells for output in cell.get("outputs", []))
assert figures == 3, f"Expected three plots, found {figures}"
for output in notebook.cells[-1].outputs:
    if output.output_type == "stream":
        print(output.text, end="")
(destination / "verification.json").write_text(json.dumps({
    "notebook": str(source.relative_to(root)),
    "student_cells": student_cell_count,
    "plots": figures,
    "python": sys.version.split()[0],
    "checks": "passed",
}, indent=2) + "\n")
print(f"Notebook executed successfully; {figures} plots. Instructor artifacts: {destination}")
