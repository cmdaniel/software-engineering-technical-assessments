from flask import Flask, request
from results_controller import ResultsController
# DM: Middleware registration helper for simulated auth checks.
from auth_middleware import register_auth_middleware, register_rate_limit_middleware

app: Flask = Flask(__name__)
controller: ResultsController = ResultsController()
# DM: Attach auth middleware globally to all incoming requests.
register_auth_middleware(app)
# DM: Enforce per-client request throttling across all routes.
register_rate_limit_middleware(app)

@app.route("/result/<identifier>", methods=["GET"])
def individual_result(identifier) -> str | dict:
    return controller.get_result(int(identifier))

@app.route("/result", methods=["POST"])
def add_result() -> dict:
    return controller.new_result(request.json)

@app.route("/scoreboard", methods=["GET"])
def scoreboard() -> dict:
    return controller.scoreboard()

@app.errorhandler(Exception)
def all_exception_handler(e):
    print(f"[ERROR] - exception ({type(e).__name__}) occurred during request handling: {e}")
    return {}, 500
