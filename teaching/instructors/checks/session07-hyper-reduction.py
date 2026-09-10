p=tests[1]
calls.update(full=0,sampled=0)
v=online_output(p)
assert calls=={'full':0,'sampled':m}
reference=float(ell@Z@np.linalg.solve(Ar,Z.T@Um@np.linalg.solve(T,source(x[points],*p))))
assert np.isclose(v,reference,rtol=1e-12)
assert tf>0 and tr>0
assert np.max(np.abs(exact-approx))<.02
