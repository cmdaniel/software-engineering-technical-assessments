from domain.election import (
    ContextResult,
    compute_constituency_winner,
    compute_overall_winner,
    compute_seats_winner,
    flat_constituency,
    map_to_parents,
)
from model.log import build_logger
from model.model import Party, ScoreboardKey
from results_service import ResultStore
from typing import Any, Callable

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

    # DM
    def get_all(self) -> list[dict]:
        return self.store.get_all()

    @staticmethod
    def pipe(
        value: ContextResult, *functions: Callable[[ContextResult], ContextResult]
    ) -> ContextResult:
        for function in functions:
            value = function(value)
        return value

    def load_data(self, context: ContextResult) -> ContextResult:
        context.constituences = map_to_parents(self.get_all())
        return context

    def scoreboard(self) -> dict:

        result = self.pipe(
            ContextResult(),
            self.load_data,
            compute_constituency_winner,
            compute_seats_winner,
            flat_constituency,
            compute_overall_winner,
        )

        return {
            **result.scoreboard.party_seats,
            ScoreboardKey.winner: Party.noone,
        }
