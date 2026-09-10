assert np.allclose(Um.T@Um,np.eye(m))
assert len(set(points))==m
assert np.allclose(Um@np.linalg.solve(T,T),Um)
assert np.all(np.array(deim_errors)<=amplification*np.array(projection_errors)+1e-11)
v=source(x,*tests[0]); approx=Um@np.linalg.solve(T,v[points])
assert np.allclose(v[points],approx[points])
assert np.isclose(amplification,np.linalg.norm(np.linalg.solve(T,np.eye(m)),2))
