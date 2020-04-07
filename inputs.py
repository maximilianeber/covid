params = {
    "r0": 2.4,
    "t_e_inc": 4.6,
    "t_i_inc": 0.5,
    "t_asy": 6,
    "t_mild": 7,
    "t_sev_pre_hos": 5,
    "t_sev_hos_rec": 25.5,
    "t_sev_hos_dec": 9,
    "p_asy": 0.3,
    "p_sev_rec": 0.044,
    "p_sev_dec": 0.009,
    "self_quar_strength": 0.0,
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
# x / 10000 = initially_infected / population_size
x = (params["initially_infected"] / params["population_size"]) * 10000
start.update({"S": 1 - x / 10000})
start.update({"E": x / 10000})

policy = {
    "policy_period0": "2020-01-12",
    "policy_period1": "2020-03-14",
    "policy_period2": "2020-03-21",
    "policy_period3": "2020-04-14",
    "policy_period4": "2020-12-31",
    "policy_strength1": 0.2,
    "policy_strength2": 0.8,
    "policy_strength3": 0.3,
}


def args_to_policy(args):
    policy = [
        (args.get("policy_period0"), 0.0),
        (args.get("policy_period1"), args.get("policy_strength1")),
        (args.get("policy_period2"), args.get("policy_strength2")),
        (args.get("policy_period3"), args.get("policy_strength3")),
        (args.get("policy_period4"), 0.0),
    ]
    return policy
