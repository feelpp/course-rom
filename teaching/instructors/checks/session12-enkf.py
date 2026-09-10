assert np.isfinite(means).all() and np.all(spreads>=0)
assert np.mean((means[1:]-truth[1:])**2)<np.mean((forecast[1:]-truth[1:])**2)
# A large scalar Gaussian ensemble approaches the independent analytic KF update.
rng=np.random.default_rng(19); X=rng.normal(0,np.sqrt(2),(1,50000))
updated=analysis(X,np.array([3.]),np.ones((1,1)),np.ones((1,1)),rng)
assert abs(updated.mean()-2)<.03
assert abs(updated.var(ddof=1)-2/3)<.03
v=np.array([1.,2.,3.]); ensemble=np.column_stack([v,v])
assert np.allclose(advance(ensemble)[:,0],advance(v))
