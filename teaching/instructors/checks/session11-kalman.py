m,p,_=update(np.array([0.]),np.array([[2.]]),np.array([3.]),np.ones((1,1)),np.array([[1.]]))
assert np.allclose(m,[2.]) and np.allclose(p,[[2/3]])
assert np.allclose(covariances,covariances.transpose(0,2,1),atol=1e-12)
assert np.min(np.linalg.eigvalsh(covariances))>=-1e-12
m,p,_=update(np.ones(2),np.eye(2),np.zeros(1),np.zeros((1,2)),R)
assert np.allclose(m,1) and np.allclose(p,np.eye(2))
assert np.mean((means[1:]-truth[1:])**2)<np.mean((forecasts[1:]-truth[1:])**2)
