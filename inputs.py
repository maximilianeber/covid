params = {
    "r0": 2.4,
    "t_incubation": 4.6,
    "t_presymptomatic": 0.5,
    "t_recovery_asymptomatic": 6,
    "t_recovery_mild": 6,
    "t_home_severe": 5,
    "t_hospital_severe_recovered": 10.4,
    "t_hospital_severe_deceased": 10.4,
    "p_asymptomatic": 0.3,
    "p_severe": 0.044,
    "p_fatal": 0.009,
    "p_self_quarantine": 0.66,
    "p_icu_given_hospital": 0.30,
    "population_size": 82790000,
    "hospital_capacity": 200000,
    "icu_capacity": 14000,
}

start = {
    "T": 0.0,
    "S": (1 - 0.006 / 10000),
    "E": 0.006 / 10000,  # assuming 50 people had just caught the virus (currently assumed to be 15/01/2020)
    "I": 0.0,
    "I_asymptomatic": 0.0,
    "I_mild": 0.0,
    "I_severe_home": 0.0,
    "I_severe_hospital": 0.0,
    "I_fatal_home": 0.0,
    "I_fatal_hospital": 0.0,
    "R_from_asymptomatic": 0.0,
    "R_from_mild": 0.0,
    "R_from_severe": 0.0,
    "Dead": 0,
    "Hypothetical R0": 2.4,
}

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
