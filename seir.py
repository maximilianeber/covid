import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import pandas as pd


class Seir(object):
    def __init__(self, params, start, dT=0.01):
        self.params = params
        self.start = start
        self.dT = dT

    def simulate(self, infection_reduction_steps):
        # Convert policy steps to daily paths
        self.policy_path = self._steps_to_path(infection_reduction_steps, dT=self.dT)

        # Initialize results with starting values
        self.results = {k: [v] for k, v in self.start.items()}
        self.results["T"] = [self.policy_path[0][0]]  # first date in policy path
        self.results["P"] = [self.policy_path[0][1]]  # first policy in policy path

        for time, infection_reduction in self.policy_path:
            self.iterate(time=time, infection_reduction=infection_reduction)

    def iterate(self, time, infection_reduction):
        """Iterate current state forward by one step with current infection_reduction"""
        # Roll forward time
        time = time + timedelta(days=self.dT)

        # Retrieve parameters
        r0 = self.params["r0"]
        t_incubation = self.params["t_incubation"]
        t_presymptomatic = self.params["t_presymptomatic"]
        t_recovery_asymptomatic = self.params["t_recovery_asymptomatic"]
        t_recovery_mild = self.params["t_recovery_mild"]
        t_hospital_severe_recovered = self.params["t_hospital_severe_recovered"]
        t_home_severe = self.params["t_home_severe"]
        t_hospital_severe_deceased = self.params["t_hospital_severe_deceased"]
        p_self_quarantine = self.params["p_self_quarantine"]
        p_asymptomatic = self.params["p_asymptomatic"]
        p_severe = self.params["p_severe"]
        p_fatal = self.params["p_fatal"]
        p_mild = 1 - p_asymptomatic - p_severe - p_fatal

        a = 1 / t_incubation
        gamma = 1 / t_presymptomatic  # but infectiuous

        S = self.results["S"][-1]
        E = self.results["E"][-1]
        I = self.results["I"][-1]
        I_asymptomatic = self.results["I_asymptomatic"][-1]
        I_mild = self.results["I_mild"][-1]
        I_severe_home = self.results["I_severe_home"][-1]
        I_severe_hospital = self.results["I_severe_hospital"][-1]
        I_fatal_home = self.results["I_fatal_home"][-1]
        I_fatal_hospital = self.results["I_fatal_hospital"][-1]
        R_from_asymptomatic = self.results["R_from_asymptomatic"][-1]
        R_from_mild = self.results["R_from_mild"][-1]
        R_from_severe = self.results["R_from_severe"][-1]
        Dead = self.results["Dead"][-1]

        # Computing the beta without any forced social distancing
        duration_infectious = (
            t_presymptomatic
            + p_asymptomatic * t_recovery_asymptomatic
            + p_mild * (1 - p_self_quarantine) * t_recovery_mild
        )
        beta = r0 / duration_infectious

        # Flows this time increment

        # Not infected
        dS = (
            -beta
            * (1 - infection_reduction)
            * (I + I_asymptomatic + (1 - p_self_quarantine) * I_mild)
            * S
        ) * self.dT

        # Non-infectiuous incubation time
        dE = (
            beta
            * (1 - infection_reduction)
            * (I + I_asymptomatic + (1 - p_self_quarantine) * I_mild)
            * S
            - a * E
        ) * self.dT

        # Infectious incubation time
        dI = (a * E - gamma * I) * self.dT

        # Asymptomatic
        dI_asymptomatic = (
            p_asymptomatic * gamma * I - (1 / t_recovery_asymptomatic) * I_asymptomatic
        ) * self.dT

        # Mild
        dI_mild = (p_mild * gamma * I - (1 / t_recovery_mild) * I_mild) * self.dT

        # B: Severe course (two steps)
        dI_severe_home = (
            p_severe * gamma * I - (1 / t_home_severe) * I_severe_home
        ) * self.dT
        dI_severe_hospital = (
            (1 / t_home_severe) * I_severe_home
            - (1 / t_hospital_severe_recovered) * I_severe_hospital
        ) * self.dT

        # C: Fatal course (two steps)
        dI_fatal_home = (
            p_fatal * gamma * I - (1 / t_home_severe) * I_fatal_home
        ) * self.dT
        dI_fatal_hospital = (
            (1 / t_home_severe) * I_fatal_home
            - (1 / t_hospital_severe_deceased) * I_fatal_hospital
        ) * self.dT

        # Final flows from courses of illness into recovery or death
        dR_from_asymptomatic = (
            (1 / t_recovery_asymptomatic) * I_asymptomatic
        ) * self.dT
        dR_from_mild = ((1 / t_recovery_mild) * I_mild) * self.dT
        dR_from_severe = (
            (1 / t_hospital_severe_recovered) * I_severe_hospital
        ) * self.dT
        dDead = ((1 / t_hospital_severe_deceased) * I_fatal_hospital) * self.dT

        # Storing simulated time self.results
        self.results["T"].append(time)
        self.results["P"].append(infection_reduction)
        self.results["S"].append(S + dS)
        self.results["E"].append(E + dE)
        self.results["I"].append(I + dI)
        self.results["I_asymptomatic"].append(I_asymptomatic + dI_asymptomatic)
        self.results["I_mild"].append(I_mild + dI_mild)
        self.results["I_severe_home"].append(I_severe_home + dI_severe_home)
        self.results["I_severe_hospital"].append(I_severe_hospital + dI_severe_hospital)
        self.results["I_fatal_home"].append(I_fatal_home + dI_fatal_home)
        self.results["I_fatal_hospital"].append(I_fatal_hospital + dI_fatal_hospital)
        self.results["R_from_asymptomatic"].append(
            R_from_asymptomatic + dR_from_asymptomatic
        )
        self.results["R_from_mild"].append(R_from_mild + dR_from_mild)
        self.results["R_from_severe"].append(R_from_severe + dR_from_severe)
        self.results["Dead"].append(Dead + dDead)

        # Current r
        r = beta * (1 - infection_reduction) * duration_infectious
        self.results["Hypothetical R0"].append(r)

    @property
    def data(self, resampling_rule="1d"):
        df = (
            pd.DataFrame.from_dict(self.results)
            .set_index("T")
            .resample(resampling_rule)
            .first()
            .assign(
                Hospitalized=lambda x: x["I_severe_hospital"] + x["I_fatal_hospital"],
                ICU=lambda x: x["Hospitalized"] * self.params["p_icu_given_hospital"],
                R_combined=lambda x: x["R_from_asymptomatic"]
                + x["R_from_mild"]
                + x["R_from_severe"],
                I_combined=lambda x: x["I"]
                + x["I_asymptomatic"]
                + x["I_mild"]
                + x["I_severe_home"]
                + x["I_severe_hospital"]
                + x["I_fatal_home"]
                + x["I_fatal_hospital"],
                Currently_infected=lambda x: x["E"]
                + x["I"]
                + x["I_asymptomatic"]
                + x["I_mild"]
                + x["I_severe_home"]
                + x["I_severe_hospital"]
                + x["I_fatal_home"]
                + x["I_fatal_hospital"],
                HospitalCapacity=self.params["hospital_capacity"],
                IcuCapacity=self.params["icu_capacity"],
                Have_or_had_virus=lambda x: x["Currently_infected"]
                + x["R_combined"]
                + x["Dead"],
            )
            .rename(columns={"P": "Reduction in new infections through policy"})
        )

        # Scale
        columns_with_individuals = [
            "Have_or_had_virus",
            "Currently_infected",
            "Hospitalized",
            "ICU",
            "Dead",
            "R_from_asymptomatic",
            "R_from_mild",
            "R_from_severe",
        ]
        df[columns_with_individuals] = (
            df[columns_with_individuals] * self.params["population_size"]
        )

        return df

    @staticmethod
    def _steps_to_path(infection_reduction_steps, dT=1):
        """Convert dictionary of infection_reduction steps to infection_reduction path and associated dates"""
        dates = [
            datetime.datetime.fromisoformat(d) for d, _ in infection_reduction_steps
        ]
        infection_reductions = [
            infection_reduction for _, infection_reduction in infection_reduction_steps
        ]
        date_path = []
        infection_reduction_path = []
        for i, x in enumerate(dates[:-1]):
            length = int((dates[i + 1] - dates[i]).days / dT)
            dates_regime = [dates[i] + timedelta(days=dT * n) for n in range(length)]
            infection_reduction_path_regime = [infection_reductions[i]] * length
            date_path.extend(dates_regime)
            infection_reduction_path.extend(infection_reduction_path_regime)
        return list(zip(date_path, infection_reduction_path))

    def plot_summary(self):
        data = self.data
        fig, ax = plt.subplots(4, 2, figsize=(12, 8))
        plt.tight_layout(pad=1.5)
        data[["Reduction in new infections through policy"]].plot(ax=ax[0, 0])
        data[["Hypothetical R0"]].plot(ax=ax[0, 1])
        data[["Have_or_had_virus"]].plot(ax=ax[1, 0])
        data[["Dead"]].plot(ax=ax[1, 1])
        data[["Currently_infected"]].plot(ax=ax[2, 0])
        data[["Hospitalized", "ICU"]].plot(ax=ax[2, 1])
        data[["S", "E", "I_combined", "R_combined"]].plot(ax=ax[3, 0])
        data[["R_from_asymptomatic", "R_from_mild", "R_from_severe", "Dead"]].plot(
            ax=ax[3, 1]
        )
        for subplot in ax.reshape(-1):
            subplot.set_xlabel("")
        plt.show()
        return None
