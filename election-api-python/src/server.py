from http.client import HTTPException
from werkzeug.exceptions import HTTPException
from flask import Flask, request
from results_controller import ResultsController

app: Flask = Flask(__name__)
controller: ResultsController = ResultsController()

@app.route("/result/<id>", methods=["GET"])
def individual_result(id) -> str | dict:
    return controller.get_result(int(id))

@app.route("/result", methods=["POST"])
def add_result() -> dict:
    return controller.new_result(request.json)

@app.route("/scoreboard", methods=["GET"])
def scoreboard() -> dict:
    return controller.scoreboard()



# DM
@app.errorhandler(OSError)
@app.errorhandler(ConnectionError)
def handle_connection_errors(err: Exception) -> tuple[dict, int]:
    return {"error": str(err)}, 503

@app.errorhandler(HTTPException)
def handle_http_errors(err: HTTPException) -> tuple[dict, int]:
    return {"error": err.description}, err.code or 500

@app.errorhandler(Exception)
def handle_unexpected_errors(err: Exception) -> tuple[dict, int]:
    return {"error": str(err)}, 500