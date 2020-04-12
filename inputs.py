params = {
    "r0": 2.4,
    "t_e_inc": 3,
    "t_i_inc": 2,
    "t_asy": 8,
    "t_mild": 8,
    "t_sev_pre_hos": 7,
    "t_sev_hos_rec": 17.7,
    "t_sev_hos_dec": 10.8,
    "p_asy": 0.2,
    "p_sev_rec": 0.08,
    "p_sev_dec": 0.0066,
    "p_icu_given_hospital": 0.30,
    "population_size": 82790000,
    "initially_infected": 50,
    "hospital_capacity": 200000,
    "icu_capacity": 14000,
}

start = {
    "T": 0.0,
    "S": 0.0,
    "E": 0.0,
    "I_inc": 0.0,
    "I_asy": 0.0,
    "I_mild": 0.0,
    "I_sev_pre_hos": 0.0,
    "I_sev_hos_rec": 0.0,
    "I_sev_hos_dec": 0.0,
    "R_asy": 0.0,
    "R_mild": 0.0,
    "R_sev": 0.0,
    "D_sev": 0,
    "Hypothetical R0": 2.4,
}

# Setting intial values of infected
# n0 / n_discretization = initially_infected / population_size
n_discretization = 10000
n0 = (params["initially_infected"] / params["population_size"]) * n_discretization
start.update({"S": 1 - n0 / n_discretization})
start.update({"E": n0 / n_discretization})

policy = {
    "policy_type": "all",
    "policy_period0": "2020-01-12",
    "policy_period1": "2020-03-14",
    "policy_period2": "2020-03-21",
    "policy_period3": "2020-04-14",
    "policy_period4": "2020-06-14",
    "policy_period5": "2020-12-31",
    "policy_strength1": 0.2,
    "policy_strength2": 0.8,
    "policy_strength3": 0.3,
    "policy_strength4": 0.3,
}


def args_to_policy(args):
    policy = [
        args.get("policy_type"),
        [(args.get("policy_period0"), 0.0),
        (args.get("policy_period1"), args.get("policy_strength1")),
        (args.get("policy_period2"), args.get("policy_strength2")),
        (args.get("policy_period3"), args.get("policy_strength3")),
        (args.get("policy_period4"), args.get("policy_strength4")),
        (args.get("policy_period5"), 0.0)],
    ]
    return policy
