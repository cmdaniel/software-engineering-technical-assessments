from domain.domain import (
    ContextResult,
    compute_constituency_winner,
    compute_is_tied,
    compute_overall_winner,
    compute_public_party_result,
    compute_seats_sum,
    flat_constituency,
    map_to_parents,
    plot_chart,
)
from results_service import ResultStore
from typing import Any, Callable


class ResultsController:

    def __init__(self) -> None:
        self.store: ResultStore = ResultStore()

    def get_result(self, id: int) -> str | dict:
        return self.store.get_result(id)

    def get_all(self) -> str | list[dict]:
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
        context.constituences = map_to_parents(self.get_all())
        return context

    def scoreboard(self) -> dict:

        result = self.pipe(
            ContextResult(),
            self.load_data,
            flat_constituency,
            compute_constituency_winner,
            compute_overall_winner,
            compute_seats_sum,
            compute_is_tied,
            compute_public_party_result,
            plot_chart,
        )

        print(result.scoreboard.party_result)

        return {
            **result.scoreboard.party_seats,
            "winner": result.scoreboard.winner,
            "sum": result.scoreboard.seats_sum,
        }
