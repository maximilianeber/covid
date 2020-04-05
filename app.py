import os
import dotenv
from flask import Flask, request
from flask_restplus import Resource, Api, reqparse
from flask_cors import CORS
from numpy import datetime_as_string
from seir import Seir
from inputs import policy, params, start, args_to_policy

app = Flask(__name__)
CORS(app, resources={r"/simulate": {"origins": "*"}})
auth = {"apikey": {"type": "apiKey", "in": "header", "name": "X-API-KEY"}}
api = Api(app, authorizations=auth)
dotenv.load_dotenv()
api_key = os.environ.get("X-API-KEY")
parser = reqparse.RequestParser()

for k, v in policy.items():
    parser.add_argument(k, type=type(v), default=v, help="Policy value for " + k)

for k, v in params.items():
    parser.add_argument(k, type=type(v), default=v, help="Parameter value for " + k)

for k, v in start.items():
    parser.add_argument(k, type=type(v), default=v, help="Starting value for " + k)


def data_to_list(df):
    data = (
        df.reset_index()[1:]  # drop initialization (first day)
        .rename(columns={"T": "time"})
        .assign(time=lambda x: datetime_as_string(x["time"], unit="D"))
        .to_dict(orient="list")
    )
    for k, v in data.items():
        data[k] = [k] + v
    return data


@api.route("/simulate")
class Simulation(Resource):
    @api.expect(parser)
    @api.doc(security="apikey")
    def post(self):
        if request.headers.get("X-API-KEY") != api_key:
            return "ERROR: Unauthorized", 401
        else:
            args = parser.parse_args(strict=True)
            policy_request = args_to_policy(args)
            params_request = {k: args[k] for k in params.keys()}
            start_request = {k: args[k] for k in start.keys()}

            seir = Seir(params=params_request, start=start_request)
            seir.simulate(policy_request)
        return data_to_list(seir.data)

    @api.expect(parser)
    @api.doc(security="apikey")
    def get(self):
        if request.headers.get("X-API-KEY") != api_key:
            return "ERROR: Unauthorized", 401
        else:
            args = parser.parse_args(strict=True)
            policy_request = args_to_policy(args)
            params_request = {k: args[k] for k in params.keys()}
            start_request = {k: args[k] for k in start.keys()}
            seir = Seir(params=params_request, start=start_request)
            seir.simulate(policy_request)
            return data_to_list(seir.data)


if __name__ == "__main__":
    app.run(debug=False)
