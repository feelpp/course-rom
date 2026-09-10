assert 0<beta<=1+1e-12
assert np.isclose(beta,beta_for(H,Z@np.diag([.1,2,10])),rtol=1e-10)
assert np.isclose(beta,beta_for(np.diag(np.linspace(.5,2,len(H)))@H,Z),rtol=1e-10)
v=np.random.default_rng(0).normal(size=n)
assert np.allclose(H@v,(H.T/h).T@(h*v))
assert np.allclose(H@estimate,y,atol=1e-10)
assert np.linalg.norm(h*Z.T@update)<1e-10
v=Z@np.arange(1,r+1)
recovered,eta,_=pbdw(H,Z,H@v)
assert np.allclose(recovered,v,atol=1e-10) and np.linalg.norm(eta)<1e-9
