import datetime
from datetime import timedelta
import pandas as pd


class Seir(object):
    def __init__(self, params, start, dT=0.01):
        self.params = params
        self.start = start
        self.dT = dT

    def simulate(self, r0_steps):
        # Convert policy steps to daily paths
        self.policy_path = self._steps_to_path(r0_steps, dT=self.dT)

        # Initialize results with starting values
        self.results = {k: [v] for k, v in self.start.items()}
        self.results["T"] = [self.policy_path[0][0]]  # first date in policy path

        for time, r0 in self.policy_path:
            self.iterate(time=time, r0=r0)

    def iterate(self, time, r0):
        """Iterate current state forward by one step with current r0"""
        # Roll forward time
        time = time + timedelta(days=self.dT)

        # Retrieve parameters
        t_infectious = self.params["t_infectious"]
        t_incubation = self.params["t_incubation"]
        t_recovery_mild = self.params["t_recovery_mild"]
        t_recovery_severe = self.params["t_recovery_severe"]
        t_hospital_lag = self.params["t_hospital_lag"]
        t_death = self.params["t_death"]
        p_severe = self.params["p_severe"]
        p_fatal = self.params["p_fatal"]

        p_mild = 1 - p_severe - p_fatal
        a = 1 / t_incubation
        gamma = 1 / t_infectious
        beta = r0 * gamma  # current beta given r0 in policy path

        # Basic SEI(R) dynamics
        S = self.results["S"][-1]
        E = self.results["E"][-1]
        I = self.results["I"][-1]  # infectious

        dS = (-beta * I * S) * self.dT
        dE = (beta * I * S - a * E) * self.dT
        dI = (a * E - gamma * I) * self.dT

        self.results["S"].append(S + dS)
        self.results["E"].append(E + dE)
        self.results["I"].append(I + dI)

        # Addititonal clinical dynamics:
        # - Infections turn into mild cases, severe cases, and fatal cases
        # - All three cases initially start at home
        # - Mild cases directly recover from home
        # - Severe case become hospitalized and recover
        # - Fatal cases become hospitalized and die
        I_mild = self.results["I_mild"][-1]
        I_severe_home = self.results["I_severe_home"][-1]
        I_severe_hospital = self.results["I_severe_hospital"][-1]
        I_fatal_home = self.results["I_fatal_home"][-1]
        I_fatal_hospital = self.results["I_fatal_hospital"][-1]
        R_from_mild = self.results["R_from_mild"][-1]
        R_from_severe = self.results["R_from_severe"][-1]
        Dead = self.results["Dead"][-1]

        # Case 1/3: Mild
        dI_mild = (p_mild * gamma * I - (1 / t_recovery_mild) * I_mild) * self.dT

        # Case 2/3: Severe
        dI_severe_home = (
            p_severe * gamma * I - (1 / t_hospital_lag) * I_severe_home
        ) * self.dT
        dI_severe_hospital = (
            (1 / t_hospital_lag) * I_severe_home
            - (1 / t_recovery_severe) * I_severe_hospital
        ) * self.dT

        # Case 3/3: Severe
        dI_fatal_home = (
            p_fatal * gamma * I - (1 / t_hospital_lag) * I_fatal_home
        ) * self.dT
        dI_fatal_hospital = (
            (1 / t_hospital_lag) * I_fatal_home - (1 / t_death) * I_fatal_hospital
        ) * self.dT

        # Final states
        dR_from_mild = ((1 / t_recovery_mild) * I_mild) * self.dT
        dR_from_severe = ((1 / t_recovery_severe) * I_severe_hospital) * self.dT
        dDead = ((1 / t_death) * I_fatal_hospital) * self.dT

        # Store simulated time series
        self.results["T"].append(time)
        self.results["I_mild"].append(I_mild + dI_mild)
        self.results["I_severe_home"].append(I_severe_home + dI_severe_home)
        self.results["I_severe_hospital"].append(I_severe_hospital + dI_severe_hospital)
        self.results["I_fatal_home"].append(I_fatal_home + dI_fatal_home)
        self.results["I_fatal_hospital"].append(I_fatal_hospital + dI_fatal_hospital)
        self.results["R_from_mild"].append(R_from_mild + dR_from_mild)
        self.results["R_from_severe"].append(R_from_severe + dR_from_severe)
        self.results["Dead"].append(Dead + dDead)

    @property
    def data(self, resampling_rule="1d"):
        df = (
            pd.DataFrame.from_dict(self.results)
            .set_index("T")
            .resample(resampling_rule)
            .first()
            .assign(
                Hospitalized=lambda x: x["I_severe_hospital"] + x["I_fatal_hospital"],
                Recovered=lambda x: x["R_from_mild"] + x["R_from_severe"],
            )
        )
        return df

    @staticmethod
    def _steps_to_path(r0_steps, dT=1):
        """Convert dictionary of R0 steps to R0 path and associated dates"""
        dates = [datetime.datetime.fromisoformat(d) for d, _ in r0_steps]
        r0s = [r0 for _, r0 in r0_steps]
        date_path = []
        r0_path = []
        for i, x in enumerate(dates[:-1]):
            length = int((dates[i + 1] - dates[i]).days / dT)
            dates_regime = [dates[i] + timedelta(days=dT * n) for n in range(length)]
            r0_path_regime = [r0s[i]] * length
            date_path.extend(dates_regime)
            r0_path.extend(r0_path_regime)
        return list(zip(date_path, r0_path))
