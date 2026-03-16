from domain.domain import (
    ContextResult,
    compute_constituency_winner,
    compute_overall_winner,
    compute_party_seats,
    compute_public_result,
    map_constituencies,
    plot_public_result,
    transform_flat_constituencies,
)
from model.model import Party
from results_service import ResultStore
from typing import Any, Callable


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
    def pipe(value: Any, *functions: Callable[[Any], Any]) -> ContextResult:
        for function in functions:
            value = function(value)
        return value

    def load_data(self, context: ContextResult) -> ContextResult:
        context.constituencies = map_constituencies(self.get_all())
        return context

    def scoreboard(self) -> dict:

        pipe_result = self.pipe(
            ContextResult(),
            self.load_data,
            transform_flat_constituencies,
            compute_constituency_winner,
            compute_party_seats,
            compute_overall_winner,
            compute_public_result,
            plot_public_result
        )

        seats = pipe_result.scoreboard.party_seats
        return {
            **seats,
            Party.winner: pipe_result.scoreboard.winner,
            Party.sum: sum(seats.values()),
            "party_result": pipe_result.scoreboard.party_result,
        }