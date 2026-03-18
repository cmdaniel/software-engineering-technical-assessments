from flask import Flask, request
from werkzeug.exceptions import HTTPException
from results_controller import ResultsController
from results_service import ResultStore

app: Flask = Flask(__name__)
controller: ResultsController = ResultsController(ResultStore())


@app.route("/result/<result_id>", methods=["GET"])
def individual_result(result_id: str) -> tuple[dict, int] | dict:
    result = controller.get_result(int(result_id))
    if result is None:
        return {"error": f"No result with id {result_id} found."}, 404
    return result


@app.route("/result", methods=["POST"])
def add_result() -> dict:
    return controller.new_result(request.json)


@app.route("/scoreboard", methods=["GET"])
def scoreboard() -> dict | str:
    return controller.scoreboard()


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
