import pandas as pd
from numba import njit, types, typed


@njit()
def sim(params, start, periods=100, dT=0.01):
    """Numba-comiled SEIR simulation"""
    rho = params["rho"]
    alpha = params["alpha"]
    beta = params["beta"]
    gamma = params["gamma"]

    T = [start["Time"]]

    S = [start["Susceptible"]]
    E = [start["Exposed"]]
    I = [start["Infected"]]
    R = [start["Removed"]]

    niter = int(periods / dT)
    for i in range(niter):

        dS = -(rho * beta * S[-1] * I[-1]) * dT
        dE = (rho * beta * S[-1] * I[-1] - alpha * E[-1]) * dT
        dI = (alpha * E[-1] - gamma * I[-1]) * dT
        dR = (gamma * I[-1]) * dT

        T.append(T[-1] + dT)

        S.append(S[-1] + dS)
        E.append(E[-1] + dE)
        I.append(I[-1] + dI)
        R.append(R[-1] + dR)

    return T, S, E, I, R


# Setup
N = 10000
start = {
    "Time": 0,
    "Susceptible": 1 - 1 / N,
    "Exposed": 1 / N,
    "Infected": 0,
    "Removed": 0,
}
params = {"alpha": 0.2, "beta": 1.75, "gamma": 0.5, "rho": 1.0}

# Typed params
params_typed = typed.Dict.empty(types.unicode_type, types.float32)
params_typed.update(params)

start_typed = typed.Dict.empty(types.unicode_type, types.float32)
start_typed.update(start)

# Run simulation
T, S, E, I, R = sim(params_typed, start_typed)

# Visualize results
results = {
    "Time": T,
    "Susceptible": S,
    "Exposed": E,
    "Infected": I,
    "Removed": R,
}
results = pd.DataFrame(results).set_index("Time")
results.plot()
results[["Infected"]].plot()
