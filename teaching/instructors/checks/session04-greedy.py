assert len(selected)==3 and len(set(selected))==3
assert np.allclose(Zg.T@Zg,np.eye(3),atol=1e-12)
assert all(not np.any(np.isclose(mu,train)) for mu in test)
for mu in test:
    u=solve_basis(Zg,mu); rho=f-(mu*K+I)@u
    assert np.linalg.norm(full(mu)-u)<=np.linalg.norm(rho)/alpha(mu)+1e-10
assert max(greedy_errors[-1])<max(greedy_errors[0])/100
assert max(pod_errors[-1])<max(pod_errors[0])/100
