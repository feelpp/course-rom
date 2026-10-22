# Instructor-only reference loop and independent diagnostics; never exported.
def reference_greedy(pairs, seed, tolerance=1e-5, rank_max=8):
    Z = append_snapshot(np.empty((n, 0)), full(*seed))
    selected = [tuple(seed)]; history = []; bases = [Z.copy()]
    while True:
        _, bounds = scan(Z, pairs)
        maximum = float(bounds.max())
        history.append((Z.shape[1], maximum))
        if maximum <= tolerance:
            status = 'tolerance met'; break
        if Z.shape[1] >= rank_max:
            status = 'rank budget reached'; break
        pair = tuple(pairs[np.argmax(bounds)])
        try:
            Z = append_snapshot(Z, full(*pair))
        except ValueError:
            status = 'dependent enrichment'; break
        selected.append(pair)
        bases.append(Z.copy())
    return dict(Z=Z, selected=selected, bases=bases, history=history, status=status)

assert n == 64 and np.allclose(G, K+M)
for name, exp in experiments.items():
    pairs = training[name]; test_pairs = validation[name]
    assert not any(np.all(np.isclose(pairs, p), axis=1).any() for p in test_pairs)
    reference = reference_greedy(pairs, recorded[name][0], tolerance=0., rank_max=5)
    assert reference['status'] == 'rank budget reached'
    assert np.allclose(reference['selected'], recorded[name])
    assert len(reference['history']) == len(recorded[name])  # Includes final scan.
    for Z, row in zip(exp['bases'], exp['rows']):
        assert np.allclose(Z.T@G@Z, np.eye(Z.shape[1]), atol=1e-9)
        assert np.all(row['error_G'] <= row['bound']+1e-10)
        # This is the Galerkin energy error, not a claim about G-error monotonicity.
        if row['rank'] > 1:
            assert np.all(row['train'] <= previous+1e-10)
        previous = row['train']
    assert exp['rows'][-1]['train'].max() < exp['rows'][0]['train'].max()/100
    # Prove the scan does not call the full solver.
    old_full = full
    def full(*args):
        raise AssertionError('The certificate scan must not query truth')
    try:
        scan(reference['Z'], pairs)
    finally:
        full = old_full
    # Explicitly check successful tolerance termination and final certificate.
    stopped = reference_greedy(pairs, recorded[name][0], tolerance=1e-5)
    assert stopped['status'] == 'tolerance met'
    assert stopped['history'][-1][1] <= 1e-5
print('Greedy independent checks: certificates, nested energy errors, selection and stopping passed.')

# Sweep diagnostics must compare the same norm with a valid pointwise certificate.
for name, results in sweep_results.items():
    pairs = sweep_pairs[name]
    assert pairs.ndim == 2 and pairs.shape[1] == 2 and len(pairs) >= 101
    for rank, result in results.items():
        assert np.isfinite(result['error']).all() and np.isfinite(result['delta']).all()
        assert np.all(result['error'] <= result['delta']+1e-10)
        j = 37  # Independently recompute a nonsampled sweep point.
        mu, g = pairs[j]
        basis = experiments[name]['bases'][rank-1]
        A = mu*K+M; load = b+g*e_right
        coeff_check = np.linalg.solve(basis.T@A@basis, basis.T@load)
        error_check = np.linalg.solve(A, load)-basis@coeff_check
        residual_check = load-A@(basis@coeff_check)
        delta_check = np.sqrt(residual_check@np.linalg.solve(G, residual_check))/min(mu, 1.)
        assert np.isclose(result['error'][j], np.sqrt(error_check@G@error_check), atol=1e-10)
        assert np.isclose(result['delta'][j], delta_check, atol=1e-10)
for name, exp in experiments.items():
    pairs = sweep_pairs[name]
    for pair in exp['selected']:
        assert np.all(pairs == pair, axis=1).any()  # Exact, not nearest-grid membership.
    for rank, result in sweep_results[name].items():
        indices = result['snapshot_indices']
        assert np.array_equal(pairs[indices], exp['selected'][:rank])
        assert result['error'][indices].max() < 1e-10
        assert result['delta'][indices].max() < 1e-9
# Off-path pairs, equal diffusivities and non-grid seeds must all be retained.
extra_1d = np.array([[.731, 0.], [.23, 0.]])
extra_2d = np.array([[.731, .17], [.731, -.12], [.23, .08]])
extra_pairs, coordinate, blocks = snapshot_sweeps(extra_1d, extra_2d)
for pair in extra_1d:
    assert np.all(extra_pairs['1 parameter: g=0'] == pair, axis=1).any()
for pair in extra_2d:
    assert np.all(extra_pairs['2 parameters'] == pair, axis=1).any()
assert np.all(np.diff(coordinate) > 0)
for block in blocks:
    section = extra_pairs['2 parameters'][block['start']:block['stop']]
    assert np.all(section[:, 1] == block['g'])
    assert section[0, 0] == .1 and section[-1, 0] == 10.
    assert np.all(np.diff(section[:, 0]) > 0)
    for mu in extra_2d[:, 0]:
        assert np.any(section[:, 0] == mu)
assert len(sweep_blocks) >= 5
for block in sweep_blocks:
    section = slice(block['start'], block['stop'])
    # Full-mu slices retain resolved errors, not a path confined to exact load spans.
    assert sweep_results['2 parameters'][5]['error'][section].max() > 1e-8
print('Parameter sweeps: matched norms and pointwise certificate checks passed.')
