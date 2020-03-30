from flask import Flask
from flask_restplus import Resource, Api, reqparse, cors
from seir import Seir
from inputs import policy, params, start, args_to_policy

app = Flask(__name__)
api = Api(app)


parser = reqparse.RequestParser()

for k, v in policy.items():
    parser.add_argument(k, type=type(v), default=v, help="Policy value for " + k)

for k, v in params.items():
    parser.add_argument(k, type=type(v), default=v, help="Parameter value for " + k)

for k, v in start.items():
    parser.add_argument(k, type=type(v), default=v, help="Starting value for " + k)


@api.route("/simulate")
class Simulation(Resource):
    @api.expect(parser)
    def post(self):
        args = parser.parse_args(strict=True)
        policy_request = args_to_policy(args)
        params_request = {k: args[k] for k in params.keys()}
        start_request = {k: args[k] for k in start.keys()}

        seir = Seir(params=params_request, start=start_request)
        seir.simulate(policy_request)
        return seir.data.to_json(orient="split")

    @api.expect(parser)
    @cors.crossdomain(origin="*")
    def get(self):
        args = parser.parse_args(strict=True)
        policy_request = args_to_policy(args)
        params_request = {k: args[k] for k in params.keys()}
        start_request = {k: args[k] for k in start.keys()}

        seir = Seir(params=params_request, start=start_request)
        seir.simulate(policy_request)
        return seir.data.to_json(orient="split")


if __name__ == "__main__":
    app.run(debug=False)
