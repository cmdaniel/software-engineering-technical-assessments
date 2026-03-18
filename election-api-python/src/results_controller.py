from domain.election import (
    ContextResult,
    compute_seats_per_party,
    parse_constituencies,
    compute_overall_winner,
    compute_seats_sum,
    flat_constituency,
    compute_public_result,
)
from model.log import build_logger
from model.model import ScoreboardKey
from results_service import ResultStore
from typing import Callable

# DM
logger = build_logger(__name__)


class ResultsController:

    def __init__(self) -> None:
        self.store: ResultStore = ResultStore()

    def get_result(self, id: int) -> str | dict:
        return self.store.get_result(id)

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

    # DM
    def get_all(self) -> list[dict]:
        return self.store.get_all()

    def scoreboard(self) -> dict:

        result = self.pipe(
            ContextResult(),
            self.load_data,
            compute_seats_per_party,
            compute_overall_winner,
            compute_seats_sum,
            flat_constituency,
            compute_public_result,
        )

        print(result.scoreboard.bonus_party_result)

        return {
            **result.scoreboard.party_seats,
            ScoreboardKey.winner: result.scoreboard.overall_winner,
            ScoreboardKey.sum: result.scoreboard.check_seats_sum,
        }
