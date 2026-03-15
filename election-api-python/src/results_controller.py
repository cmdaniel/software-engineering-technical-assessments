from domain.domain import ContextResult, map_constituencies
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
    def pipe(value: Any, *functions: Callable[[Any], Any]) -> Any:
        for function in functions:
            value = function(value)
        return value

    def load_data(self, context: ContextResult) -> ContextResult:
        context.constituencies = map_constituencies(self.get_all())
        return context

    def scoreboard(self) -> dict:

        result = self.pipe(
            ContextResult(),
            self.load_data,
        )

        return {Party.LD: 1, Party.LAB: 4, Party.winner: Party.noone}
