from dataclasses import dataclass
from results_service import ResultStore
from model import (
    Party,
    MIN_VOTES,
    PartyResult,
    FlatResult,
    Result,
    map_results,
    flat_results,
)
from collections import defaultdict


class AppValidationError(Exception):
    """Raised when input validation fails."""


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

    def scoreboard(self) -> dict:
        try:
            payload = self.get_all()

            if not payload or isinstance(payload, str):
                raise AppValidationError("payload is required")

            flatten_results = flat_results(payload)

            grouped_winners = defaultdict(list)
            for item in flatten_results:
                if item.seat_winner_party == item.party:
                    grouped_winners[item.party].append(item)

            result_dict = {
                party: len(seats) for party, seats in grouped_winners.items()
            }
            top_party, top_seats = max(
                result_dict.items(), key=lambda item: item[1], default=("noone", 0)
            )

            is_tied = list(result_dict.values()).count(top_seats) > 1

            winner = top_party if top_seats >= MIN_VOTES and not is_tied else "noone"

            total_seats = sum(result_dict.values())

            total_votes = sum(item.votes for item in flatten_results)

            grouped_party = defaultdict(list)
            for item in flatten_results:
                grouped_party[item.party].append(item)

            party_result = {
                party: {
                    "votes": sum(item.votes for item in items),
                    "share": round(
                        sum(item.votes for item in items) / total_votes * 100, 2
                    ),
                }
                for party, items in grouped_party.items()
            }

            total_shares = sum(item["share"] for item in party_result.values())

            return {
                **result_dict,
                Party.WINNER: winner,
                Party.SUM: total_seats,
                "party_result": party_result,
            }

        except AttributeError as err:
            print(err)
            pass
        except Exception as err:
            print(err)
            pass
        finally:
            self.reset()

        return {}
