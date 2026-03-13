from dataclasses import dataclass, field
from results_service import ResultStore
from model import FlatResult, Party, Result, map_results, flat_result
from collections import defaultdict
from collections.abc import Callable
from typing import Any


@dataclass()
class ContextResult:
    results: list[Result] = field(default_factory=list)
    flattened_results: list[FlatResult] = field(default_factory=list)
    groupped_by_party: defaultdict[str, list[FlatResult]] = field(
        default_factory=lambda: defaultdict(list)
    )
    scoreboard: dict = field(default_factory=dict)


class AppValidationError(Exception):
    """Raised when input validation fails."""


class ResultsController:
    def __init__(self) -> None:
        self.store: ResultStore = ResultStore()

    def get_all(self) -> list[dict]:
        return self.store.get_all()

    def get_result(self, identifier: int) -> str | dict:
        return self.store.get_result(identifier)

    def new_result(self, result: dict) -> dict:
        self.store.new_result(result)
        return {}

    def reset(self) -> None:
        self.store.reset()

    def pipe(self, value: Any, *functions: Callable[[Any], Any]) -> Any:
        for function in functions:
            value = function(value)
        return value

    def load_data(self) -> ContextResult:
        self.context = ContextResult(results=map_results(self.get_all()))
        return self.context

    def flat_data(self, context: ContextResult) -> ContextResult:
        context.flattened_results = flat_result(context.results)
        return context

    def group_by_party(self, context: ContextResult) -> ContextResult:
        context.groupped_by_party = defaultdict(list)
        for item in context.flattened_results:
            context.groupped_by_party[item.party].append(item)
        return context

    def compute_scoreboard(self, context: ContextResult) -> dict:
        context.scoreboard = {
            party: len(item) for party, item in context.groupped_by_party.items()
        }
        return context.scoreboard

    def scoreboard(self) -> dict:
        try:
            scoreboard_result = self.pipe(
                self.load_data,
                self.flat_data,
                self.group_by_party,
                self.compute_scoreboard,
            )

            # if not payload:
            #     raise AppValidationError("payload is required")

            return {**scoreboard_result, Party.WINNER: "noone"}

        except AttributeError as err:
            print(err)
            pass
        except Exception as err:
            print(err)
            pass

        return {}
        # return {Party.LD: 1, Party.LAB: 4, Party.WINNER: "noone"}
