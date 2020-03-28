from flask import Flask
from flask_restplus import Resource, Api, reqparse
from seir import Seir


app = Flask(__name__)
api = Api(app)

# Starting Values
params = {
    "beta": 0.5,
    "t_incubation": 5.5,
    "t_presymptomatic": 1.5,
    "t_recovery_asymptomatic": 5,
    "t_recovery_mild": 14,
    "t_recovery_severe": 30.5,
    "t_death": 14,
    "t_hospital_lag": 5,
    "p_asymptomatic": 0.3,
    "p_severe": 0.18,
    "p_fatal": 0.02,
    "p_self_quarantine": 0.5,
    "p_icu_given_hospital": 0.20,
}

start = {
    "T": 0.0,
    "S": (1 - 1 / 10000),
    "E": 1 / 10000,
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
}

# Argument parser
parser = reqparse.RequestParser()
parser.add_argument('policy_period0', type=str, help='Beginning of simulation', )
parser.add_argument('policy_period1', type=str, help='Beginning of lockdown')
parser.add_argument('policy_period2', type=str, help='Beginning of relaxation')
parser.add_argument('policy_period3', type=str, help='End of simulation')
parser.add_argument('policy_strength1', type=float, help='Policy strength in lockdown period')
parser.add_argument('policy_strength2', type=float, help='Policy strength in relaxation period')


@api.route('/hello')
class Index(Resource):
    def get(self):
        return {'hello': 'world'}


# curl -X POST "http://127.0.0.1:5000/simulate" -d '{"policy_period1": "2020-03-21", "policy_strength1":0.7, "policy_period2": "2020-07-21", "policy_strength2": 0.3}'  -H "Content-Type: application/json"

@api.route('/simulate')
class Simulation(Resource):
    @api.expect(parser)
    def post(self):
        args = parser.parse_args(strict=True)
        policy = [
            (args.get("policy_period0") or "2020-02-28", 0.0),
            (args.get("policy_period1") or "2020-03-21", args.get("policy_strength1") or .8),
            (args.get("policy_period2") or "2020-07-21", args.get("policy_strength2") or .4),
            (args.get("policy_period2") or "2020-12-31", 0.0),
        ]
        seir = Seir(params, start)
        seir.simulate(policy)
        return seir.data.to_json(orient="split")
    
    @api.expect(parser)
    def get(self):
        args = parser.parse_args(strict=True)
        policy = [
            (args.get("policy_period0") or "2020-02-28", 0.0),
            (args.get("policy_period1") or "2020-03-21", args.get("policy_strength1") or .8),
            (args.get("policy_period2") or "2020-07-21", args.get("policy_strength2") or .4),
            (args.get("policy_period2") or "2020-12-31", 0.0),
        ]
        seir = Seir(params, start)
        seir.simulate(policy)
        return seir.data.to_json(orient="split")


if __name__ == '__main__':
    app.run(debug=False)
