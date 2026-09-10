assert n==1333 and len(set(sensor_indices))==4
assert truth_Bi not in train_Bi and forecast_Bi not in train_Bi
assert np.allclose(Z.T@(M@Z),np.eye(r),atol=1e-7)
A=operator(.07); u=truth[:,1]
assert np.linalg.norm((M+dt*A)@u-dt*f*inputs[0])<1e-9
assert np.allclose(ell@estimate,(ell@Z)@coeff)
assert np.allclose(estimate[sensor_indices],Z[sensor_indices]@coeff)
assert mass_rmse(estimate[:,1:]-truth[:,1:])<mass_rmse(reduced_forecast[:,1:]-truth[:,1:])
assert np.isfinite(estimate).all()
