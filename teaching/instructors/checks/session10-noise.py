y=H@truth+np.random.default_rng(2).normal(0,sigma_noise,len(H))
xi=.1
state,eta,d=pbdw(H,Z,y,xi)
assert np.allclose(H@state-y,-xi*d,atol=1e-9)
assert np.linalg.norm(h*Z.T@eta)<1e-9
assert chosen_xi==np.argmin(validation_errors.mean(axis=1))
assert np.isfinite(test_errors).all()
# Independently solve the unconstrained least-squares problem in (a,d).
Q=H.T/h; A=H@Q; B=H@Z
L=np.linalg.cholesky(A)
ls=np.block([[B,A],[np.zeros((len(H),r)),np.sqrt(xi)*L.T]])
coeff=np.linalg.lstsq(ls,np.r_[y,np.zeros(len(H))],rcond=None)[0]
assert np.allclose(state,Z@coeff[:r]+Q@coeff[r:],atol=1e-7)
