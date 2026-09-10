"""Execute sessions 2–3 from fresh kernels and check numerical invariants.

Only student cells enter the starter preview. Added reference checks stay outside
Antora and all student downloads. All inputs come from the built release.
"""
from pathlib import Path
import hashlib
import json
import sys
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'build/course-release'
OUTPUT.mkdir(parents=True, exist_ok=True)
CHECKS = {
'session02-galerkin-pod': r'''
# PCA covariance directions and normalization versus weighted centered POD.
assert np.allclose(Sc.mean(axis=1), 0, atol=1e-14)
covariance = Sc @ Sc.T / (len(mu_train)-1)
variance = sigma_c**2 * len(mu_train) / (h * (len(mu_train)-1))
assert np.allclose(covariance @ Uc[:, :3], Uc[:, :3] * variance[:3], atol=1e-12)
assert np.isclose(np.sum(pca_variance_ratio), 1)
# The affine centered Galerkin equations retain the mean and its output.
centered_basis = Uc[:, :2] / np.sqrt(h)
for mu in mu_test:
    A = mu*K + I
    coeff = np.linalg.solve(centered_basis.T @ A @ centered_basis,
                            centered_basis.T @ (f - A @ u_mean))
    centered_state = u_mean + centered_basis @ coeff
    assert np.linalg.norm(centered_basis.T @ (f - A @ centered_state)) < 1e-8
    output = h*np.sum(u_mean) + (h*centered_basis.T @ np.ones(n)) @ coeff
    assert np.isclose(output, h*np.sum(centered_state))
# Independent POD identities in the declared metric.
assert not any(np.isclose(a, b) for a in mu_train for b in mu_test)
assert np.allclose(h * Z.T @ Z, np.eye(r), atol=1e-12)
projected = Z @ (h * Z.T @ S)
actual_tail = np.sqrt(h / len(mu_train)) * np.linalg.norm(S - projected, 'fro')
assert np.isclose(actual_tail, training_tail, rtol=1e-7, atol=1e-13)
assert np.allclose(Mr, np.eye(r) / h, atol=1e-11)
max_errors = []
for rank in (1, 2, 3):
    basis = U[:, :rank] / np.sqrt(h)
    local_errors = []
    for mu in mu_test:
        A = mu*K + I
        coeff = np.linalg.solve(basis.T @ A @ basis, basis.T @ f)
        truth, approx = full(mu), basis @ coeff
        error = truth - approx
        assert np.linalg.norm(basis.T @ (f - A @ approx)) < 1e-8
        projected_state = basis @ (h * basis.T @ truth)
        projection_error = truth - projected_state
        # Galerkin is optimal in the A-energy norm, projection in G.
        assert error @ A @ error <= projection_error @ A @ projection_error + 1e-11
        assert np.linalg.norm(projection_error) <= np.linalg.norm(error) + 1e-11
        local_errors.append(np.sqrt(h) * np.linalg.norm(error))
    max_errors.append(max(local_errors))
assert max_errors[2] < max_errors[1] < max_errors[0], max_errors
assert max_errors[2] < max_errors[0] / 100
print('PCA/POD checks passed: covariance, centering, affine ROM, weighted tail, orthogonality, held-out Galerkin optimality and rank comparison.')
print('Maximum held-out errors for ranks 1, 2, 3:', max_errors)
''',
'session03-error-estimation': r'''
# Direct spectral calculation is only a reference check, never an online dependency.
assert np.isclose(lambda_min_K, np.linalg.eigvalsh(K)[0], rtol=1e-10)
assert np.all(np.array(bounds) >= np.array(errors) - 1e-10)
assert np.all(np.array(weak_bounds) >= np.array(bounds) - 1e-10)
assert np.all(np.array(output_errors) <= h*np.sqrt(n)*np.array(bounds) + 1e-10)
for rank in (1, 2, 3):
    basis = U[:, :rank] / np.sqrt(h)
    columns = np.column_stack([f, K @ basis, basis])
    _, factor = np.linalg.qr(columns, mode='reduced')
    for mu in mu_test:
        A = mu*K + I
        coeff = np.linalg.solve(basis.T @ A @ basis, basis.T @ f)
        approx = basis @ coeff
        direct = np.linalg.norm(f - A @ approx)
        efficient = np.linalg.norm(factor @ np.r_[1., -mu*coeff, -coeff])
        assert np.isclose(direct, efficient, rtol=2e-5, atol=2e-10)
        error = np.linalg.norm(full(mu) - approx)
        assert efficient / alpha_exact(mu) >= error - 1e-10
# For an error in the lowest eigenmode, the exact-coercivity bound is sharp.
e = np.sin(np.pi*x)
for mu in (0.1, 1., 10.):
    rho = (mu*K+I) @ e
    assert np.isclose(np.linalg.norm(rho)/alpha_exact(mu), np.linalg.norm(e), rtol=1e-10)
    assert np.isclose((np.linalg.norm(rho)/np.sqrt(h))/(alpha_exact(mu)/h),
                      np.sqrt(h)*np.linalg.norm(e), rtol=1e-10)
print('Certification checks passed: spectrum, state/output coverage, QR residual, sharp eigenmode and metric scaling.')
'''
}
for name, check in CHECKS.items():
    source = ROOT / 'public/course-rom/_attachments/labs' / f'{name}.ipynb'
    notebook = nbformat.read(source, as_version=4)
    nbformat.validate(notebook)
    student_cells = len(notebook.cells)
    notebook.cells.append(nbformat.v4.new_code_cell(check))
    NotebookClient(notebook, timeout=90, kernel_name='python3',
                   resources={'metadata': {'path': str(OUTPUT)}}).execute()
    nbformat.write(notebook, OUTPUT / f'{name}-reference.ipynb')
    for out in notebook.cells[-1].outputs:
        if out.output_type == 'stream': print(out.text, end='')
    student = nbformat.from_dict(notebook)
    student.cells = student.cells[:student_cells]
    nbformat.write(student, OUTPUT / f'{name}-executed.ipynb')
    html, _ = HTMLExporter(template_name='classic').from_notebook_node(student)
    preview = OUTPUT / f'{name}-starter.html'
    preview.write_text(html)
    count = sum('image/png' in out.get('data', {}) for cell in student.cells for out in cell.get('outputs', []))
    assert count == (2 if name.startswith('session02') else 1)
    (OUTPUT / f'{name}-verification.json').write_text(json.dumps({
        'checks': 'passed', 'python': sys.version.split()[0], 'plots': count,
        'notebook_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'preview_sha256': hashlib.sha256(preview.read_bytes()).hexdigest(),
        'requirements_sha256': hashlib.sha256((ROOT / 'requirements-course.txt').read_bytes()).hexdigest(),
    }, indent=2) + '\n')
    print(f'{name}: executed {student_cells} student cells; {count} plots; independent checks passed.')
