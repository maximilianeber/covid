import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import pandas as pd


class Seir(object):
    def __init__(self, params, start, dT=0.01):
        self.params = params
        self.start = start
        self.dT = dT

    def simulate(self, policy_specs):

        # Store type of policy: all vs sym only
        self.policy_type = policy_specs[0]

        # Convert policy steps to daily paths
        self.policy_path = self._steps_to_path(policy_specs[1], dT=self.dT)

        # Initialize results with starting values
        self.results = {k: [v] for k, v in self.start.items()}
        self.results["T"] = [self.policy_path[0][0]]  # first date in policy path
        self.results["P"] = [self.policy_path[0][1]]  # first policy in policy path

        for time, policy_strength in self.policy_path:
            self.iterate(time=time, policy_strength=policy_strength)

    def iterate(self, time, policy_strength):
        """Iterate current state forward by one step with current policy_strength"""
        time = time + timedelta(days=self.dT)  # roll forward time

        # Retrieve parameters
        
        # Policy type
        if self.policy_type=="sym":
            
            policy_strength_all = 0
            policy_strength_sym = policy_strength
            
        else:
            
            policy_strength_all = policy_strength
            policy_strength_sym = 0  
            
        # Basic repreproduction number
        r0 = self.params["r0"]

        # Non-infectious incubation period
        t_e_inc = self.params["t_e_inc"]
        # Infectious incubation period
        t_i_inc = self.params["t_i_inc"]
        # Duration illness asymptomatic course
        t_asy = self.params["t_asy"]
        # Duration illness mild course
        t_mild = self.params["t_mild"]
        # Duration until severe cases enter the hospital
        t_sev_pre_hos = self.params["t_sev_pre_hos"]
        # Duration hospital stay severe cases who recover
        t_sev_hos_rec = self.params["t_sev_hos_rec"]
        # Duration hospital stay severe cases who decease
        t_sev_hos_dec = self.params["t_sev_hos_dec"]

        # Share of asymptomatic cases
        p_asy = self.params["p_asy"]
        # Share of severe cases who whill recover
        p_sev_rec = self.params["p_sev_rec"]
        # Share of severe cases who will decease, mortality rate
        p_sev_dec = self.params["p_sev_dec"]
        # Share of mild cases
        p_mild = 1 - p_asy - p_sev_rec - p_sev_dec

        # Model equations

        # Quantities

        # Susceptible
        S = self.results["S"][-1]
        # In non-infectious incubation time
        E = self.results["E"][-1]
        # In infectious incubation time
        I_inc = self.results["I_inc"][-1]
        # Infectious, asymptomatic course
        I_asy = self.results["I_asy"][-1]
        # Infectious, mild course
        I_mild = self.results["I_mild"][-1]
        # Infectious, severe course, before hospital stay
        I_sev_pre_hos = self.results["I_sev_pre_hos"][-1]
        # Infectious, severe course, subsquent stay at hospital with recovery
        I_sev_hos_rec = self.results["I_sev_hos_rec"][-1]
        # Infectious, severe course, subsquent stay at hospital deceased
        I_sev_hos_dec = self.results["I_sev_hos_dec"][-1]
        # Recovered, asymptomatic course
        R_asy = self.results["R_asy"][-1]
        # Recovered, mild course
        R_mild = self.results["R_mild"][-1]
        # Recovered, severe course
        R_sev = self.results["R_sev"][-1]
        # Deceased, severe course
        D_sev = self.results["D_sev"][-1]

        # Computing the baseline beta without any intervention
        average_duration_infectious_no_intervention = (
            t_i_inc
            + p_asy * t_asy
            + p_mild * t_mild
            + (p_sev_rec + p_sev_dec) * t_sev_pre_hos
        )

        beta = r0 / average_duration_infectious_no_intervention

        # Flows

        # Susceptible
        dS = (
            (1 - policy_strength_all)
            * (-beta)
            * (I_inc + I_asy + (1 - policy_strength_sym) * (I_mild + I_sev_pre_hos))
            * S
        ) * self.dT

        # Non-infectiuous incubation time
        dE = (
            (1 - policy_strength_all)
            * beta
            * (I_inc + I_asy + (1 - policy_strength_sym) * (I_mild + I_sev_pre_hos))
            * S
            - (1 / t_e_inc) * E
        ) * self.dT

        # Infectious incubation time
        dI_inc = ((1 / t_e_inc) * E - (1 / t_i_inc) * I_inc) * self.dT

        # Asymptomatic course
        dI_asy = ((1 / t_i_inc) * p_asy * I_inc - (1 / t_asy) * I_asy) * self.dT

        # Mild course
        dI_mild = ((1 / t_i_inc) * p_mild * I_inc - (1 / t_mild) * I_mild) * self.dT

        # Severe course, pre hospital
        dI_sev_pre_hos = (
            (1 / t_i_inc) * (p_sev_rec + p_sev_dec) * I_inc
            - (1 / t_sev_pre_hos) * I_sev_pre_hos
        ) * self.dT

        # Severe course, hospital, recovering
        dI_sev_hos_rec = (
            (1 / t_sev_pre_hos) * (p_sev_rec / (p_sev_rec + p_sev_dec)) * I_sev_pre_hos
            - (1 / t_sev_hos_rec) * I_sev_hos_rec
        ) * self.dT

        # Severe course, hospital, fatal
        dI_sev_hos_dec = (
            (1 / t_sev_pre_hos) * (p_sev_dec / (p_sev_rec + p_sev_dec)) * I_sev_pre_hos
            - (1 / t_sev_hos_dec) * I_sev_hos_dec
        ) * self.dT

        # Recovered asymptomatic
        dR_asy = ((1 / t_asy) * I_asy) * self.dT

        # Recovered from mild
        dR_mild = ((1 / t_mild) * I_mild) * self.dT

        # Recovered from severe
        dR_sev = ((1 / t_sev_hos_rec) * I_sev_hos_rec) * self.dT

        # Deceased from severe
        dD_sev = ((1 / t_sev_hos_dec) * I_sev_hos_dec) * self.dT

        # Storing updates
        self.results["T"].append(time)
        self.results["P"].append(policy_strength)
        self.results["S"].append(S + dS)
        self.results["E"].append(E + dE)
        self.results["I_inc"].append(I_inc + dI_inc)
        self.results["I_asy"].append(I_asy + dI_asy)
        self.results["I_mild"].append(I_mild + dI_mild)
        self.results["I_sev_pre_hos"].append(I_sev_pre_hos + dI_sev_pre_hos)
        self.results["I_sev_hos_rec"].append(I_sev_hos_rec + dI_sev_hos_rec)
        self.results["I_sev_hos_dec"].append(I_sev_hos_dec + dI_sev_hos_dec)
        self.results["R_asy"].append(R_asy + dR_asy)
        self.results["R_mild"].append(R_mild + dR_mild)
        self.results["R_sev"].append(R_sev + dR_sev)
        self.results["D_sev"].append(D_sev + dD_sev)
        # Computing the hypothetical R0 with the current interventions in place
        average_duration_infectious_with_intervention = (
            t_i_inc
            + p_asy * t_asy
            + (1 - policy_strength_sym)
            * (p_mild * t_mild + (p_sev_rec + p_sev_dec) * t_sev_pre_hos)
        )

        r = beta * (1 - policy_strength_all) * average_duration_infectious_with_intervention
        # print(
        #    f"{average_duration_infectious_no_intervention:.2f} vs. {average_duration_infectious_with_intervention:.2f}"
        # )  # for debugging
        self.results["Hypothetical R0"].append(r)

    @property
    def data(self, resampling_rule="1d"):
        df = (
            pd.DataFrame.from_dict(self.results)
            .set_index("T")
            .resample(resampling_rule)
            .first()
            .assign(
                Hospitalized=lambda x: x["I_sev_hos_rec"] + x["I_sev_hos_dec"],
                ICU=lambda x: x["Hospitalized"] * self.params["p_icu_given_hospital"],
                HospitalizedExclIcu=lambda x: x["Hospitalized"] - x["ICU"],
                Recovered=lambda x: x["R_asy"] + x["R_mild"] + x["R_sev"],
                Infectious=lambda x: x["I_inc"]
                + x["I_asy"]
                + x["I_mild"]
                + x["I_sev_pre_hos"]
                + x["I_sev_hos_rec"]
                + x["I_sev_hos_dec"],
                Infected=lambda x: x["E"] + x["Infectious"],
                HospitalCapacity=self.params["hospital_capacity"],
                IcuCapacity=self.params["icu_capacity"],
                Cases=lambda x: x["Infected"] + x["Recovered"] + x["D_sev"],
            )
            .rename(
                columns={
                    "P": "Reduction in new infections through policy",
                    "S": "Susceptible",
                    "E": "Exposed",
                    "R_asy": "Recovered from asymptomatic",
                    "R_mild": "Recovered from mild",
                    "R_sev": "Recovered from severe",
                    "D_sev": "Deceased",
                    "HospitalizedExclIcu": "Hospitalized excl. ICU"
                }
            )
        )

        # Scale
        columns_with_individuals = [
            "Susceptible",
            "Cases",
            "Exposed",
            "Infectious",
            "Infected",
            "Hospitalized",
            "Hospitalized excl. ICU",
            "ICU",
            "Deceased",
            "Recovered from asymptomatic",
            "Recovered from mild",
            "Recovered from severe",
            "Recovered",
        ]
        df[columns_with_individuals] = (
            df[columns_with_individuals] * self.params["population_size"]
        )

        return df

    @staticmethod
    def _steps_to_path(policy_strength_steps, dT=1):
        """Convert dictionary of policy_strength steps to policy_strength path and associated dates"""
        isodates, policy_strengths = zip(*policy_strength_steps)
        dates = [datetime.datetime.fromisoformat(d) for d in isodates]
        date_path = []
        policy_strength_path = []
        for i, x in enumerate(dates[:-1]):
            length = int((dates[i + 1] - dates[i]).days / dT)
            dates_regime = [dates[i] + timedelta(days=dT * n) for n in range(length)]
            policy_strength_path_regime = [policy_strengths[i]] * length
            date_path.extend(dates_regime)
            policy_strength_path.extend(policy_strength_path_regime)
        return list(zip(date_path, policy_strength_path))

    def plot_summary(self):
        data = self.data
        fig, ax = plt.subplots(4, 2, figsize=(12, 8))
        plt.tight_layout(pad=1.5)
        data[["Reduction in new infections through policy"]].plot(ax=ax[0, 0])
        data[["Hypothetical R0"]].plot(ax=ax[0, 1])
        data[["Cases"]].plot(ax=ax[1, 0])
        data[["Deceased"]].plot(ax=ax[1, 1])
        data[["Infectious"]].plot(ax=ax[2, 0])
        data[["Hospitalized excl. ICU", "ICU"]].plot(ax=ax[2, 1])
        data[["Susceptible", "Exposed", "Infectious", "Recovered", "Deceased"]].plot(
            ax=ax[3, 0]
        )
        data[
            [
                "Recovered from asymptomatic",
                "Recovered from mild",
                "Recovered from severe",
                "Deceased",
            ]
        ].plot(ax=ax[3, 1])
        for subplot in ax.reshape(-1):
            subplot.set_xlabel("")
        plt.show()
        return None
