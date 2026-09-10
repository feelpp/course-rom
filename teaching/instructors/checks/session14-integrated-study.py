assert len(rows)==3 and np.isfinite(np.array(rows)).all()
assert all(row[-1]>0 for row in rows)
assert np.allclose(Zall[:,:6].T@(M@Zall[:,:6]),np.eye(6),atol=1e-7)
# The independently held-out checkpoint is executable without changing the filter.
target=trajectory(.085)
observed=target[sensor_indices,1:]+np.random.default_rng(150).normal(0,.005,(4,steps))
C,_,_,_=reduced_filter(Zall[:,:6],observed,sensor_indices)
assert np.isfinite(C).all()
assert mass_rmse(Zall[:,:6]@C[:,1:]-target[:,1:])<.3
