# Validate the supplied starter and preserve the student implementation work.
assert S.shape == (120, 27)
assert len(params) == 27 and len(tests) == 3
assert np.isfinite(S).all() and np.all(S >= .1)
assert np.allclose(S[:, 0], source(x, *params[0]))
assert all(p not in params for p in tests)
for function, arguments in [
    (interpolation_coefficients, (np.ones((3, 1)), np.array([0]), np.ones(1))),
    (new_eim_direction, (S,)),
    (eim, (S, 8)),
    (eim_online, (np.ones((n, 1)), np.array([0]), tests[0])),
]:
    try:
        function(*arguments)
    except NotImplementedError:
        pass
    else:
        raise AssertionError('A student EIM exercise unexpectedly contains its solution')
print('EIM starter checked: supplied data valid; exercise functions remain incomplete.')
