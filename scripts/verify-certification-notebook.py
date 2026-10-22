"""Execute the generated certification notebook and independently test its API.

Reference checks are appended only in memory, never to the student notebook.
Build the executable Antora site before running this verifier.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import sys

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'materials/modules/ROOT/pages/certification/residual-bound.adoc'
export = ROOT / 'public/rom/_attachments/certification/residual-bound.ipynb'
notebook = nbformat.read(export, as_version=4)
nbformat.validate(notebook)
assert notebook.metadata.course.source_sha256 == hashlib.sha256(source.read_bytes()).hexdigest()
assert sum(cell.cell_type == 'code' for cell in notebook.cells) == 3
student_count = len(notebook.cells)
notebook.cells.append(nbformat.v4.new_code_cell(r'''
# Independent fixtures: nonorthonormal basis, non-diagonal metric, affine loads.
rng = np.random.default_rng(20261022)
for n_test, r_test in ((12, 2), (6, 4)):
    Q = rng.normal(size=(n_test, n_test))
    metric = Q.T @ Q + np.eye(n_test)
    metric_chol = np.linalg.cholesky(metric)
    v = rng.normal(size=n_test)
    rank_one = np.outer(v, v)
    loads = rng.normal(size=(n_test, 2))
    basis = rng.normal(size=(n_test, r_test))  # Deliberately not G-orthonormal.
    ell = rng.normal(size=n_test)
    api = AffineCertificate((metric, rank_one), loads.T, basis, metric, ell)
    assert api.offline_sizes['factor_shape'] == (min(n_test, 2+2*r_test), 2+2*r_test)
    for mu in (0.2, 1., 3.):
        ta, tf = (mu, 0.7), (1., -0.4)
        alpha = mu
        gamma = mu + 0.7 * np.linalg.norm(np.linalg.solve(metric_chol, v))**2
        answer = api.query(ta, tf, alpha, gamma)
        A = mu*metric + 0.7*rank_one
        f = loads @ tf
        uh = np.linalg.solve(A, f)
        ur = basis @ answer['a']
        err = uh - ur
        rho = f - A @ ur
        eG, ea = np.sqrt(err @ metric @ err), np.sqrt(err @ A @ err)
        residual = np.sqrt(rho @ np.linalg.solve(metric, rho))
        assert np.isclose(answer['residual_norm'], residual, rtol=1e-9, atol=1e-11)
        assert np.isclose(f @ uh - answer['compliant_output'], ea**2, rtol=1e-8, atol=1e-11)
        for actual, low, high in ((eG, answer['lower_G'], answer['delta_G']),
                                  (ea, answer['lower_a'], answer['delta_a']),
                                  (ea**2, answer['lower_s'], answer['delta_s'])):
            assert low <= actual + 1e-10 and actual <= high + 1e-10
        assert abs(ell @ err) <= answer['delta_output'] + 1e-10
        assert np.isclose(answer['delta_s'] / ea**2, (answer['delta_a'] / ea)**2)
    zero = api.query((1., 0.7), (0., 0.), 1.)
    assert np.all(zero['a'] == 0)
    assert zero['residual_norm'] == zero['delta_G'] == zero['delta_a'] == zero['delta_s'] == 0
    for invalid in (0., -1., np.nan, np.inf):
        try:
            api.query((1., 0.7), (1., -0.4), invalid)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid coercivity bound accepted')

# Repeated affine components produce dependent residual columns; QR must allow this.
I = np.eye(10)
basis = I[:, :2]
load = np.arange(1., 11.)
dependent = AffineCertificate((I, 2*I), (load, load), basis, I)
ans = dependent.query((1., 0.5), (1., 0.), 2., 2.)
truth = load / 2
error = truth - basis @ ans['a']
assert np.isclose(ans['delta_G'], np.linalg.norm(error))
assert np.isclose(ans['delta_s'], 2*np.dot(error, error))

# An online call cannot fall back to a full-dimensional solve.
original_solve = np.linalg.solve
def reduced_only_solve(A, b):
    assert A.shape[0] != 10, 'Online path attempted a full solve'
    return original_solve(A, b)
try:
    np.linalg.solve = reduced_only_solve
    dependent.query((1., 0.5), (1., 0.), 2.)
finally:
    np.linalg.solve = original_solve
print('Independent API checks passed: both norms, compliant/general outputs, dependent columns, rectangular QR, zero residual and reduced-only online solves.')
'''))

with TemporaryDirectory() as tmp:
    kernel = Path(tmp) / 'kernel'
    kernel.mkdir()
    (kernel / 'kernel.json').write_text(json.dumps({
        'argv': [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
        'display_name': 'Certification verification', 'language': 'python',
    }))

    class LocalKernelSpecManager(KernelSpecManager):
        def find_kernel_specs(self):
            return {'python3': str(kernel)}

    class LocalKernelManager(KernelManager):
        def __init__(self, **kwargs):
            super().__init__(kernel_spec_manager=LocalKernelSpecManager(), **kwargs)

    NotebookClient(notebook, timeout=60, kernel_manager_class=LocalKernelManager,
                   resources={'metadata': {'path': tmp}}).execute()

outputs = [o for c in notebook.cells if c.cell_type == 'code' for o in c.outputs]
assert not any(o.output_type == 'error' for o in outputs)
assert sum('image/png' in o.get('data', {}) for o in outputs) == 1
text = '\n'.join(o.get('text', '') for o in outputs)
assert 'Offline/online certification: verified norms, outputs, bounds and effectivities.' in text
assert 'Independent API checks passed:' in text
notebook.cells = notebook.cells[:student_count]
out = ROOT / 'build/course-release/certification-executed.ipynb'
out.parent.mkdir(parents=True, exist_ok=True)
nbformat.write(notebook, out)
print(text)
print(f'Certification notebook: three student cells, one figure; independent checks passed.\n{out}')
