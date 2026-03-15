from domain.domain import (
    ContextResult,
    compute_constituencies_winner,
    compute_overall_winner,
    compute_parties_result,
    compute_party_seats,
    compute_seats_sum,
    map_to_constituency,
)
from model.log import build_logger
from model.model import Party
from results_service import ResultStore
from typing import Any, Callable

logger = build_logger(__name__)
logger.info("service started")


class ResultsController:
    def __init__(self) -> None:
        self.store: ResultStore = ResultStore()

    def get_result(self, id: int) -> str | dict:
        return self.store.get_result(id)

    def get_all(self) -> list[dict]:
        return self.store.get_all()

    def new_result(self, result: dict) -> dict:
        self.store.new_result(result)
        return {}

    def reset(self) -> None:
        self.store.reset()

    @staticmethod
    def pipe(value: Any, *functions: Callable[[Any], Any]) -> Any:
        for function in functions:
            value = function(value)
        return value

    def load_data(self, context: str | ContextResult) -> str | ContextResult:
        if isinstance(context, str):
            raise TypeError(context)
        try:
            context.constituencies = map_to_constituency(self.get_all())
            return context
        except Exception as ex:
            logger.error(ex)
            return str(ex)

    def scoreboard(self) -> dict:
        try:
            logger.info("scoreboard started")

            pipe_run = self.pipe(
                ContextResult(),
                self.load_data,
                compute_constituencies_winner,
                compute_party_seats,
                compute_overall_winner,
                compute_seats_sum,
                compute_parties_result,
            )

            if isinstance(pipe_run, str):
                raise TypeError(pipe_run)

            scoreboard = pipe_run.scoreboard
            logger.info("scoreboard succesfully generated")
            return {
                **scoreboard.party_seats,
                Party.WINNER: scoreboard.overall_winner,
                Party.SUM: scoreboard.seats_sum,
            }
        except Exception as ex:
            logger.error(ex)

        return {}
