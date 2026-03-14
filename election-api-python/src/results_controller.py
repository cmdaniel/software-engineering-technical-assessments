from dataclasses import dataclass, field

from matplotlib import pyplot as plt
from results_service import ResultStore
from model import FlatResult, Party, Result, map_results, flat_result, MIN_VOTES
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
    winner: str = "noone"
    party_results: dict = field(default_factory=dict)


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

    def load_data(self, context: ContextResult) -> ContextResult:
        context.results = map_results(self.get_all())
        return context

    def flat_data(self, context: ContextResult) -> ContextResult:
        context.flattened_results = flat_result(context.results)
        return context

    def group_by_party(self, context: ContextResult) -> ContextResult:
        context.groupped_by_party = defaultdict(list)
        for item in context.flattened_results:
            if item.party == item.seat_winner_party:
                context.groupped_by_party[item.party].append(item)
        return context

    def compute_party_results(self, context: ContextResult) -> ContextResult:
        total_votes = sum(item.votes for item in context.flattened_results)
        party_results = {
            item.party: {
                "votes": sum(
                    i.votes for i in context.flattened_results if item.party == i.party
                ),
                "share": round(
                    sum(
                        i.votes
                        for i in context.flattened_results
                        if item.party == i.party
                    )
                    / total_votes
                    * 100,
                    2,
                ),
            }
            for item in context.flattened_results
        }
        context.party_results = party_results
        return context

    def compute_scoreboard(self, context: ContextResult) -> dict:
        context.scoreboard = {
            party: len(item) for party, item in context.groupped_by_party.items()
        }
        return context.scoreboard

    def compute_winner(self, scoreboard: dict) -> dict:
        winner_party = max(scoreboard, key=lambda item: scoreboard[item], default={})
        winner_party = (
            winner_party if scoreboard[winner_party] >= MIN_VOTES else "noone"
        )
        seats_sum = sum(scoreboard.values())
        return {**scoreboard, Party.WINNER: winner_party, Party.SUM: seats_sum}

    def plot_scoreboard(self, scoreboard: dict) -> dict:
        plt.bar(range(len(scoreboard)), list(scoreboard.values()))
        plt.xticks(range(len(scoreboard)), [str(key) for key in scoreboard.keys()])
        plt.xlabel("Category")
        plt.ylabel("Value")
        plt.title("Bar Chart")
        plt.show()
        return scoreboard

    def scoreboard(self) -> dict:
        try:
            scoreboard_result = self.pipe(
                ContextResult(),
                self.load_data,
                self.flat_data,
                self.group_by_party,
                self.compute_party_results,
                self.compute_scoreboard,
                self.plot_scoreboard,
                self.compute_winner,
            )

            return {**scoreboard_result}

        except AttributeError as err:
            print(err)
            pass
        except Exception as err:
            print(err)
            pass

        return {}
