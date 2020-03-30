params = {
    "beta": 0.35,
    "t_incubation": 5.5,
    "t_presymptomatic": 1.5,
    "t_recovery_asymptomatic": 5,
    "t_recovery_mild": 14,
    "t_recovery_severe": 30.5,
    "t_death": 14,
    "t_hospital_lag": 5,
    "p_asymptomatic": 0.3,
    "p_severe": 0.09,
    "p_fatal": 0.01,
    "p_self_quarantine": 0.5,
    "p_icu_given_hospital": 0.20,
    "population_size": 82790000,
    "hospital_capacity": 200000,
    "icu_capacity": 14000,
}

start = {
    "T": 0.0,
    "S": (1 - 0.024 / 10000),
    "E": 0.024 / 10000,  # assumng 200 people where infected in the beginning
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
    "R0": 0,
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
