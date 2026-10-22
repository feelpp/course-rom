# Instructor-only answer loop; reference checks never enter student notebooks.
def reference_pod_greedy(parameters, seed=.01, tolerance=.05, rank_max=8):
    Z = enrich_trajectory(np.empty((n, 0)), seed)
    selected = [float(seed)]; history = []
    while True:
        bounds = scan_fin(Z, parameters)
        maximum = float(bounds.max())
        history.append((Z.shape[1], maximum))
        if maximum <= tolerance:
            status = 'tolerance met'; break
        if Z.shape[1] >= rank_max:
            status = 'rank budget reached'; break
        Bi = float(parameters[np.argmax(bounds)])
        try:
            Z = enrich_trajectory(Z, Bi)
        except ValueError:
            status = 'dependent enrichment'; break
        selected.append(Bi)
    return dict(Z=Z, selected=selected, history=history, status=status)

assert n == 1333 and len(set(sensor_indices)) == 4
assert steps == 100 and np.isclose(dt, .1) and np.isclose(times[-1], 10.)
assert np.count_nonzero(inputs) == 1 and inputs[0] == 1.
assert np.allclose(ell, M@np.ones(n))  # Original PDF output convention.
assert truth_Bi not in train_Bi and forecast_Bi not in train_Bi
previous = float('inf')
for basis, row, bounds in zip(fin_bases, fin_rows, fin_bounds):
    assert np.allclose(basis.T@(M@basis), np.eye(basis.shape[1]), atol=1e-8)
    assert row['projection'] <= previous+1e-10
    previous = row['projection']
    for Bi, bound in zip(train_Bi, bounds):
        truth_reference = fin_truth[float(Bi)]
        reduced_state = basis@predict_fin(project_fin(basis), Bi)
        assert max_mass_error(truth_reference-reduced_state) <= bound+1e-9
assert fin_rows[-1]['train'] < fin_rows[0]['train']/10
reference = reference_pod_greedy(train_Bi, tolerance=0., rank_max=len(recorded_Bi))
assert np.allclose(reference['selected'], recorded_Bi)
assert len(reference['history']) == len(recorded_Bi)
assert reference['status'] == 'rank budget reached'
old_trajectory = trajectory
def trajectory(*args, **kwargs):
    raise AssertionError('No full trajectory is permitted in a certificate scan')
try:
    scan_fin(reference['Z'], train_Bi)
finally:
    trajectory = old_trajectory
# Discrete balance under the *different* validation control, not impulse input.
for k in (1, 20, 100):
    balance = ((M+dt*operator(truth_Bi))@truth[:, k]
               - M@truth[:, k-1]-dt*f*prediction_inputs[k-1])
    assert np.linalg.norm(balance) < 1e-9
assert np.allclose(ell@(Z@coeff_prediction), project_fin(Z)['ell']@coeff_prediction)
assert np.allclose(estimate[sensor_indices], Z[sensor_indices]@coeff)
assert mass_rmse(estimate[:, 1:]-truth[:, 1:]) < mass_rmse(reduced_forecast[:, 1:]-truth[:, 1:])
assert np.isfinite(estimate).all()
print('Thermal-fin independent checks: time stepping, projection, certificates and selection passed.')
