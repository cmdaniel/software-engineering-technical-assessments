from domain.domain import (
    ContextResult,
    compute_constituency_winners,
    compute_overall_winner,
    compute_party_results,
    compute_scoreboard,
    compute_scoreboard_party_seats,
    compute_seats_sum,
    flat_constituencies,
    map_to_parents,
    plot_chart,
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
        context.constituencies = map_to_parents(self.get_all())
        return context

    def scoreboard(self) -> dict:

        result = self.pipe(
            ContextResult(),
            self.load_data,
            compute_constituency_winners,
            compute_scoreboard_party_seats,
            compute_overall_winner,
            flat_constituencies,
            compute_party_results,
            compute_seats_sum,
            compute_scoreboard,
            plot_chart,
        )

        print(result.scoreboard.party_result)
        
        return {
            **result.scoreboard.party_seats,
            Party.winner: result.scoreboard.winner,
            Party.sum: result.scoreboard.seats_sum,
        }
