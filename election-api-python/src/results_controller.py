from domain.domain import (
    ContextResult,
    compute_overall_winner,
    compute_party_results,
    compute_party_seats,
    flat_constituencies,
    parse_constituencies,
)
from model.log import build_logger
from model.model import ScoreboardKey
from results_service import ResultRepository
from typing import Callable


logger = build_logger(__name__)


class ResultsController:

    def __init__(self, store: ResultRepository) -> None:
        self.store = store

    def get_result(self, result_id: int) -> dict | None:
        return self.store.get_result(result_id)

    def get_all(self) -> list[dict]:
        return self.store.get_all()

    def new_result(self, result: dict) -> dict:
        self.store.new_result(result)
        return {}

    def reset(self) -> None:
        self.store.reset()

    @staticmethod
    def pipe(
        value: ContextResult, *functions: Callable[[ContextResult], ContextResult]
    ) -> ContextResult:
        for function in functions:
            value = function(value)
        return value

    def load_data(self, context: ContextResult) -> ContextResult:
        context.constituencies = parse_constituencies(self.get_all())
        return context

    def scoreboard(self) -> dict:
        result = self.pipe(
            ContextResult(),
            self.load_data,
            compute_party_seats,
            compute_overall_winner,
            flat_constituencies,
            compute_party_results,
        )

        logger.debug("Party results: %s", result.scoreboard.party_result)

        return {
            **result.scoreboard.party_seats,
            ScoreboardKey.winner: result.scoreboard.winner,
            ScoreboardKey.sum: result.scoreboard.seats_sum,
        }
