from dataclasses import dataclass, field
from matplotlib import pyplot as plt
from results_service import ResultStore
from model import (
    Party,
    MIN_VOTES,
    FlatResult,
    Result,
    map_results,
    flat_results,
)
from collections import defaultdict
from collections.abc import Callable
from typing import Any
import pandas as pd


class PayloadingError(Exception):
    """Raised when input validation fails."""


@dataclass
class ScoreboardContext:
    flatten_results: list[FlatResult]
    grouped_winners: dict[str, list[FlatResult]] = field(default_factory=dict)
    result_dict: dict[str, int] = field(default_factory=dict)
    top_party: str = "noone"
    top_seats: int = 0
    winner: str = "noone"
    total_seats: int = 0
    total_votes: int = 0
    grouped_party: dict[str, list[FlatResult]] = field(default_factory=dict)
    party_result: dict[str, dict[str, int | float]] = field(default_factory=dict)
    total_shares: float = 0.0
    df_results: pd.DataFrame = field(default_factory=pd.DataFrame)


class ResultsController:
    def __init__(self) -> None:
        self.store: ResultStore = ResultStore()

    def get_result(self, identifier: int) -> str | dict:
        return self.store.get_result(identifier)

    def new_result(self, result: dict) -> dict:
        self.store.new_result(result)
        return {}

    def get_all(self) -> str | list[Result]:
        raw_items = self.store.get_all()
        mapped_items = map_results(raw_items)
        return mapped_items

    def reset(self) -> None:
        self.store.reset()

    def pipe(self, value: Any, *functions: Callable[[Any], Any]) -> Any:
        for function in functions:
            value = function(value)
        return value

    def data_load(self) -> str | list[Result]:
        payload = self.get_all()
        if not payload or isinstance(payload, str):
            raise PayloadingError("payload is required")
        return payload

    def flatten_results(self, payload: list[Result]) -> list[FlatResult]:
        return flat_results(payload)

    def grouped_winners(self, flatten_results: list[FlatResult]) -> ScoreboardContext:
        grouped_winners = defaultdict(list)
        for item in flatten_results:
            if item.seat_winner_party == item.party:
                grouped_winners[item.party].append(item)
        return ScoreboardContext(
            flatten_results=flatten_results,
            grouped_winners=dict(grouped_winners),
        )

    def compute_result_dict(self, context: ScoreboardContext) -> ScoreboardContext:
        context.result_dict = {
            party: len(seats) for party, seats in context.grouped_winners.items()
        }
        context.top_party, context.top_seats = max(
            context.result_dict.items(),
            key=lambda item: item[1],
            default=("noone", 0),
        )
        return context

    def compute_winner(self, context: ScoreboardContext) -> ScoreboardContext:
        is_tied = list(context.result_dict.values()).count(context.top_seats) > 1
        context.winner = (
            context.top_party
            if context.top_seats >= MIN_VOTES and not is_tied
            else "noone"
        )
        context.total_seats = sum(context.result_dict.values())
        context.total_votes = sum(item.votes for item in context.flatten_results)
        return context

    def compute_party_result(self, context: ScoreboardContext) -> ScoreboardContext:
        grouped_party = defaultdict(list)
        for item in context.flatten_results:
            grouped_party[item.party].append(item)

        context.grouped_party = dict(grouped_party)
        context.party_result = {
            party: {
                "votes": votes,
                "share": (
                    round(votes / context.total_votes * 100, 2)
                    if context.total_votes
                    else 0
                ),
            }
            for party, items in context.grouped_party.items()
            for votes in [sum(item.votes for item in items)]
        }
        return context

    def compute_total_shares(self, context: ScoreboardContext) -> ScoreboardContext:
        context.total_shares = sum(
            item["share"] for item in context.party_result.values()
        )
        return context

    def convert_to_df(self, context: ScoreboardContext) -> ScoreboardContext:
        df = pd.DataFrame(context.party_result)
        context.df_results = df
        return context

    def plot_chart(self, context: ScoreboardContext) -> ScoreboardContext:
        totals = context.result_dict
        plt.bar(range(len(totals)), list(totals.values()))
        plt.xticks(range(len(totals)), [str(key) for key in totals.keys()])
        plt.xlabel("Category")
        plt.ylabel("Value")
        plt.title("Bar Chart")
        plt.show()

        return context

    def format_scoreboard(self, context: ScoreboardContext) -> dict:
        return {
            **context.result_dict,
            Party.WINNER: context.winner,
            Party.SUM: context.total_seats,
            "party_result": context.party_result,
        }

    def scoreboard(self) -> dict:
        try:
            return self.pipe(
                self.data_load(),
                self.flatten_results,
                self.grouped_winners,
                self.compute_result_dict,
                self.compute_winner,
                self.compute_party_result,
                self.compute_total_shares,
                self.convert_to_df,
                self.plot_chart,
                self.format_scoreboard,
            )

        except PayloadingError as err:
            print(err)
            pass
        except AttributeError as err:
            print(err)
            pass
        except Exception as err:
            print(err)
            pass
        finally:
            self.reset()

        return {}
