assert len(set(points))==8
assert np.allclose(np.triu(T,1),0,atol=1e-12)
assert np.allclose(np.diag(T),1)
assert np.allclose(Q@np.linalg.solve(T,T),Q)
for p in tests:
    v=source(x,*p); approx=Q@np.linalg.solve(T,v[points])
    assert np.allclose(approx[points],v[points],atol=1e-12)
assert max(errors)<.5
