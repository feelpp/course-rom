# Validate the given POD setup without supplying DEIM selection or online answers.
assert S.shape == (120, 27) and Um.shape == (120, 8)
assert np.allclose(Um.T@Um, np.eye(m))
assert np.allclose((U*singular_values)@Vt, S)
assert all(p not in params for p in tests)
for function, arguments in [
    (deim, (Um,)),
    (deim_online, (Um, np.array([0]), tests[0])),
]:
    try:
        function(*arguments)
    except NotImplementedError:
        pass
    else:
        raise AssertionError('A student DEIM exercise unexpectedly contains its solution')
print('DEIM starter checked: POD data valid; selection and online tasks remain incomplete.')
