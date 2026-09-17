"""Numerically check worked note examples and norm/covariance identities.

Run with the course Python environment. These checks deliberately include a
non-diagonal state metric, so incorrect Cholesky orientations are detectable.
No full-order reference is used as an input to a reduced prediction.
"""
from itertools import product
from pathlib import Path
import re

import numpy as np

ROOT = Path(__file__).resolve().parents[1] / 'materials/modules/ROOT/pages'

# Execute the complete, standalone worked examples as published in the notes.
examples = {}
for name in ('foundations/riesz.adoc', 'reduction/galerkin.adoc', 'reduction/pod.adoc'):
    namespace = {}
    blocks = re.findall(r'\[source,python\]\n----\n(.*?)\n----',
                        (ROOT / name).read_text(), re.DOTALL)
    assert blocks, name
    for block in blocks:
        exec(compile(block, name, 'exec'), namespace)
    examples[name] = namespace
riesz = examples['foundations/riesz.adoc']
assert np.allclose(riesz['z'], [2/3, -1/3])
assert np.isclose(riesz['dual_norm'], np.sqrt(2/3))
rb = examples['reduction/galerkin.adoc']
assert np.allclose(rb['Kr'], [[2, -1], [-1, 2]])
assert np.allclose(rb['Mr'], np.diag([1, 2]))
assert np.isclose(rb['predict'](1., rb['Kr'], rb['Mr'], rb['fr'], rb['ellr']), 20/33)
assert np.isclose(rb['ell'] @ np.linalg.solve(rb['K'] + np.eye(3), rb['f']), 13/21)
for mu in (.1, 1., 3., 10.):
    A = mu * rb['K'] + np.eye(3)
    Z, f = rb['Z'], rb['f']
    a = np.linalg.solve(Z.T @ A @ Z, Z.T @ f)
    direct_output = rb['ell'] @ (Z @ a)
    assert np.isclose(rb['predict'](mu, rb['Kr'], rb['Mr'], rb['fr'], rb['ellr']), direct_output)
    error = np.linalg.solve(A, f) - Z @ a
    residual = f - A @ Z @ a
    alpha, gamma = np.linalg.eigvalsh(A)[[0, -1]]
    assert np.linalg.norm(residual) / gamma <= np.linalg.norm(error) + 1e-14
    assert np.linalg.norm(error) <= np.linalg.norm(residual) / alpha + 1e-14

rng = np.random.default_rng(709)
base = rng.normal(size=(9, 9))
G = base.T @ base + np.eye(9)
L = np.linalg.cholesky(G).T
B = rng.normal(size=(9, 4))
B[:, 3] = B[:, 0] - 2*B[:, 1]  # QR formula must allow dependent columns.
Y = np.linalg.solve(L.T, B)
_, T = np.linalg.qr(Y, mode='reduced')
for _ in range(8):
    c = rng.normal(size=4)
    rho = B @ c
    z = np.linalg.solve(G, rho)
    dual = np.sqrt(rho @ z)
    assert np.isclose(np.linalg.norm(T @ c), dual)
    v = z / dual
    assert np.isclose(v @ G @ v, 1)
    assert np.isclose(rho @ v, dual)  # supremum is attained
    for trial in rng.normal(size=(20, 9)):
        assert abs(rho @ trial) <= dual * np.sqrt(trial @ G @ trial) + 1e-12

# The effectivity table and its zero-error exclusion.
A = np.diag([1., 4.])
for e, expected in [(np.array([1., 0.]), 1), (np.array([0., 1.]), 4),
                    (np.array([0., 1e-6]), 4)]:
    residual = A @ e
    eta = np.linalg.norm(residual) / np.linalg.norm(e)
    assert np.isclose(eta, expected)
    assert np.isclose(np.linalg.norm(residual) / .1 / np.linalg.norm(e), 10*eta)

# PBDW stability via normalized spaces agrees with a generalized Rayleigh quotient.
Z = rng.normal(size=(9, 2))
H = rng.normal(size=(4, 9))
Q = np.linalg.solve(G, H.T)
UV, RV = np.linalg.qr(L @ Z, mode='reduced')
UW, _ = np.linalg.qr(L @ Q, mode='reduced')
beta = np.linalg.svd(UW.T @ UV, compute_uv=False)[-1]
Aobs, Bobs = H @ Q, H @ Z
background_metric = Z.T @ G @ Z
projection_metric = Bobs.T @ np.linalg.solve(Aobs, Bobs)
Cbg = np.linalg.cholesky(background_metric)
normalized = np.linalg.solve(Cbg, projection_metric)
normalized = np.linalg.solve(Cbg, normalized.T).T
assert np.isclose(beta**2, np.linalg.eigvalsh(normalized)[0])
assert np.allclose(Q.T @ G, H)
# Background reproduction and regularized stationarity.
truth_coeff = np.array([.3, -.8])
y = H @ Z @ truth_coeff
for xi in (0., .2):
    saddle = np.block([[Aobs + xi*np.eye(4), Bobs], [Bobs.T, np.zeros((2, 2))]])
    sol = np.linalg.solve(saddle, np.r_[y, np.zeros(2)])
    d, a = sol[:4], sol[4:]
    eta = Q @ d
    estimate = Z @ a + eta
    assert np.allclose(estimate, Z @ truth_coeff)
    assert np.allclose(H @ estimate - y, -xi*d)
    assert np.allclose(Z.T @ G @ eta, 0)
# Correlated-noise whitening.
R = np.array([[2., .4], [.4, 1.]])
C = np.linalg.cholesky(R)
whitened = np.linalg.solve(C, R)
whitened = np.linalg.solve(C, whitened.T).T
assert np.allclose(whitened, np.eye(2))

# DEIM's oblique-projector norm identity, with a resolved but oblique example.
U, _ = np.linalg.qr(rng.normal(size=(9, 3)), mode='reduced')
P = np.eye(9)[:, [0, 2, 5]]
Ts = P.T @ U
D = U @ np.linalg.solve(Ts, P.T)
inverse_norm = 1 / np.linalg.svd(Ts, compute_uv=False)[-1]
assert np.isclose(np.linalg.norm(D, 2), inverse_norm)
assert np.isclose(np.linalg.norm(np.eye(9) - D, 2), inverse_norm)
for f in rng.normal(size=(10, 9)):
    assert np.linalg.norm(f - D @ f) <= inverse_norm * np.linalg.norm(f - U @ U.T @ f) + 1e-12

# Exact expectation over all independent unit-variance scalar perturbations.
# Gaussianity is unnecessary for this second-moment identity.
forecast = np.array([-np.sqrt(2), 0., np.sqrt(2)])
gain = 2/3
analysis_variances = []
for eps in product((-1., 1.), repeat=3):
    analysis = forecast + gain*(3. + np.array(eps) - forecast)
    analysis_variances.append(np.var(analysis, ddof=1))
assert np.isclose(np.mean(analysis_variances), 2/3)
assert np.isclose(np.var(forecast + gain*(3.-forecast), ddof=1), 2/9)
assert np.isclose((1-gain)**2 * 2 + gain**2, 2/3)
print('Mathematical notes verified: worked Riesz and affine prediction examples, bounds/effectivity, weighted QR, PBDW stability, whitening, DEIM norm and EnKF covariance.')

# The explicit projection example distinguishes reconstruction, testing and projection.
Z = rb['Z']
u = np.array([1., 2., 0.])
a = np.linalg.solve(Z.T @ Z, Z.T @ u)
assert np.allclose(a, [1, 1])
assert np.allclose(Z @ a, [1, 1, 1])
assert not np.allclose(Z @ (Z.T @ u), Z @ a)
P = Z @ np.linalg.solve(Z.T @ Z, Z.T)
assert np.allclose(P @ P, P)
for mu in (.1, 1., 10.):
    A = mu * rb['K'] + np.eye(3)
    f = rb['f']
    truth = np.linalg.solve(A, f)
    state = Z @ np.linalg.solve(Z.T @ A @ Z, Z.T @ f)
    error = truth - state
    rho = f - A @ state
    assert np.allclose(Z.T @ rho, 0)
    assert np.isclose(f @ (truth-state), error @ A @ error)
    assert f @ error >= -1e-14
    alpha = np.linalg.eigvalsh(A)[0]
    assert f @ error <= rho @ rho / alpha + 1e-14
    if mu == 1.:
        assert np.isclose(f @ error, 3/77)
# Exact snapshot reproduction after changing reduced coordinates.
A = rb['K'] + np.eye(3)
truth = np.linalg.solve(A, rb['f'])
z = truth[:,None] / np.linalg.norm(truth)
assert np.allclose(z @ np.linalg.solve(z.T @ A @ z, z.T @ rb['f']), truth)
raw = np.array([[1., 1.], [0., 1e-3]])
assert np.isclose(np.linalg.cond(raw.T @ raw), 4e6, rtol=1e-6)
orthogonal, _ = np.linalg.qr(raw)
assert np.isclose(np.linalg.cond(orthogonal.T @ orthogonal), 1)
# Sampling is reproducible, respects the interval and separates training/validation.
train, validation = rb['mu_train'], rb['mu_validation']
assert np.allclose(train[1:] / train[:-1], (10/.1)**(1/11))
assert not np.any(np.isclose(train[:,None], validation))
assert np.all((rb['mu_test'] > .1) & (rb['mu_test'] < 10))
# The weighted correlation worked example has unequal weights and a non-diagonal G.
pod = examples['reduction/pod.adoc']
assert np.isclose(pod['w'].sum(), 1)
assert np.allclose(pod['lam'], pod['sigma']**2)
# Geometry mapping: interface fixed, right boundary moves, inverse has the plus sign.
for mu in (-.2, 0., .5):
    scale = 1 + 3*mu
    assert np.isclose(scale*(2/3)-2*mu, 2/3)
    assert np.isclose(scale-2*mu, 1+mu)
    x = .8
    xtilde = scale*x-2*mu
    assert np.isclose((xtilde+2*mu)/scale, x)
    J = np.diag([scale, 1.])
    tensor = np.linalg.det(J) * np.linalg.inv(J) @ np.linalg.inv(J).T
    assert np.allclose(tensor, np.diag([1/scale, scale]))
print('Restored RB/POD details verified: projection coordinates, compliant output, conditioning, sampling, weighted correlation and reference geometry.')
