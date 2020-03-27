import numpy
import pandas as pd


def simulator(parameters, start, periods, dT):

    """Modified SEIR model"""

    # Retrieving parameters

    # List with integers which denote days when r_0 changes, e.g. [25, 55, ...]
    r_0_days = parameters["r_0_days"]
    # List with floats for the r_0 values associated with these changes,
    # e.g. [3.5, 2.5, ...]
    r_0_values = parameters["r_0_values"]

    t_infectious = parameters["t_infectious"]
    t_incubation = parameters["t_incubation"]
    t_recovery_mild = parameters["t_recovery_mild"]
    t_recovery_severe = parameters["t_recovery_severe"]
    t_hospital_lag = parameters["t_hospital_lag"]
    t_death = parameters["t_death"]
    p_severe = parameters["p_severe"]
    p_fatal = parameters["p_fatal"]

    a = 1 / t_incubation
    gamma = 1 / t_infectious

    p_mild = 1 - p_severe - p_fatal

    niter = int(periods / dT)

    series = {
        "T": [start["T"]],
        "S": [start["S"]],
        "E": [start["E"]],
        "I": [start["I"]],
        "I_mild": [start["I_mild"]],
        "I_severe_home": [start["I_severe_home"]],
        "I_severe_hospital": [start["I_severe_hospital"]],
        "I_fatal_home": [start["I_fatal_home"]],
        "I_fatal_hospital": [start["I_fatal_hospital"]],
        "R_from_mild": [start["R_from_mild"]],
        "R_from_severe": [start["R_from_severe"]],
        "Dead": [start["Dead"]],
    }

    # Creation of the r_0 path (a list of length niter / a step function of r_0 values)
    r_0_path = []
    previous_day = 0
    for cc in range(len(r_0_days)):

        r_0_path += (r_0_days[cc] - previous_day) * [r_0_values[cc]]
        previous_day = r_0_days[cc]

    ## Iterations
    for i in range(niter):

        # Computing the current beta
        beta = r_0_path[int(i * dT)] / t_infectious

        ## Current model iteration

        T = series["T"][-1]
        S = series["S"][-1]
        E = series["E"][-1]
        I = series["I"][-1]
        I_mild = series["I_mild"][-1]
        I_severe_home = series["I_severe_home"][-1]
        I_severe_hospital = series["I_severe_hospital"][-1]
        I_fatal_home = series["I_fatal_home"][-1]
        I_fatal_hospital = series["I_fatal_hospital"][-1]
        R_from_mild = series["R_from_mild"][-1]
        R_from_severe = series["R_from_severe"][-1]
        Dead = series["Dead"][-1]

        dS = (-beta * I * S) * dT
        dE = (beta * I * S - a * E) * dT
        dI = (a * E - gamma * I) * dT

        # Flows into three mutually exclusive courses of the illness
        # A: Mild course
        dI_mild = (p_mild * gamma * I - (1 / t_recovery_mild) * I_mild) * dT

        # B: Severe course (two steps)
        dI_severe_home = (
            p_severe * gamma * I - (1 / t_hospital_lag) * I_severe_home
        ) * dT
        dI_severe_hospital = (
            (1 / t_hospital_lag) * I_severe_home
            - (1 / t_recovery_severe) * I_severe_hospital
        ) * dT

        # C: Fatal course (two steps; in this version, fatal cases follow the same
        # route as severe cases: first home, then hospital. This tries to ensure that
        # they show up in the hospital statistics of the model as well)
        dI_fatal_home = (p_fatal * gamma * I - (1 / t_hospital_lag) * I_fatal_home) * dT
        dI_fatal_hospital = (
            (1 / t_hospital_lag) * I_fatal_home - (1 / t_death) * I_fatal_hospital
        ) * dT

        # Final flows from courses of ilness into recovery or death
        dR_from_mild = ((1 / t_recovery_mild) * I_mild) * dT
        dR_from_severe = ((1 / t_recovery_severe) * I_severe_hospital) * dT
        dDead = ((1 / t_death) * I_fatal_hospital) * dT

        ## Storing simulated time series

        series["T"].append(T + dT)
        series["S"].append(S + dS)
        series["E"].append(E + dE)
        series["I"].append(I + dI)
        series["I_mild"].append(I_mild + dI_mild)
        series["I_severe_home"].append(I_severe_home + dI_severe_home)
        series["I_severe_hospital"].append(I_severe_hospital + dI_severe_hospital)
        series["I_fatal_home"].append(I_fatal_home + dI_fatal_home)
        series["I_fatal_hospital"].append(I_fatal_hospital + dI_fatal_hospital)
        series["R_from_mild"].append(R_from_mild + dR_from_mild)
        series["R_from_severe"].append(R_from_severe + dR_from_severe)
        series["Dead"].append(Dead + dDead)

    return series
