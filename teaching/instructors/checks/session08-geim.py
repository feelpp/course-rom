assert len(set(chosen))==5
assert np.allclose(Hdict@np.ones(n),1)
assert np.allclose(np.triu(T,1),0,atol=1e-11)
assert np.allclose(np.diag(T),1)
assert np.allclose(H@clean,y,atol=1e-12)
assert np.sqrt(h)*np.linalg.norm(noisy-clean)<=gain*np.linalg.norm(noise)+1e-12
coeff=np.arange(Q.shape[1])+1
assert np.allclose(reconstruct(H@(Q@coeff)),Q@coeff)
