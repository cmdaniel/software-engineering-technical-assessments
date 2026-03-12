from collections import defaultdict

from pandas.core.groupby import DataFrameGroupBy
from results_service import ResultStore
from dataclasses import dataclass
import pandas as pd
import matplotlib.pyplot as plt

@dataclass
class PartyResult:
    party: str
    votes: int
    share: int

@dataclass
class Result:
    id: int
    name: str
    seqNo: int
    partyResults: list[PartyResult]

@dataclass
class FlatResult:
    id: int
    name: str
    seqNo: int
    party: str
    votes: int
    share: int

class ResultsController:

    def __init__(self) -> None:
        self.result_store: ResultStore = ResultStore()

    def get_result(self, identifier: int) -> str | dict:
        return self.result_store.get_result(identifier)

    def new_result(self, result: dict) -> dict:
        self.result_store.new_result(result)
        return {}

    def get_result_all(self) -> str | list[Result]:
        untyped_results = self.result_store.get_all()
        results = []
        if isinstance(untyped_results, list):
            for item in untyped_results:
                party_results = [
                    PartyResult(**party_result) for party_result in item["partyResults"]
                ]
                results.append(
                    Result(
                        id=item["id"],
                        name=item["name"],
                        seqNo=item["seqNo"],
                        partyResults=party_results,
                    )
                )
        return results

    def reset(self) -> None:
        self.result_store.reset()

    def scoreboard(self) -> dict:
        results = self.get_result_all()
        if not isinstance(results, list):
            return {}

        # Seats per party
        seats_by_party: dict[str, int] = {}
        total_seats = 0

        for constituency_result in results:
            seat_winner = max(
                constituency_result.partyResults,
                key=lambda item: item.votes,
                default=None,
            )
            if seat_winner is None:
                continue

            seats_by_party[seat_winner.party] = (
                seats_by_party.get(seat_winner.party, 0) + 1
            )
            total_seats += 1

        is_valid = total_seats == sum(seats_by_party.values())
        if not is_valid:
            return {}

        # Votes and Share per party
        flat_results: list[FlatResult] = []
        for constituency_result in results:
            row = {
                "id": constituency_result.id,
                "name": constituency_result.name,
                "seqNo": constituency_result.seqNo,
            }
            for party_result in constituency_result.partyResults:
                row["party"] = party_result.party
                row["votes"] = party_result.votes
                row["share"] = party_result.share

            flat_results.append(FlatResult(**row))

        grouped = defaultdict(list)
        for result in flat_results:
            grouped[result.party].append(result)

        total_votes = sum(item.votes for item in flat_results)
        
        party_results = {
            party: {
                "sum_votes": sum(row.votes for row in rows),
                "sum_share": round(sum(row.votes for row in rows)/total_votes * 100, 2),
            }
            for party, rows in grouped.items()
        }
        
        party_with_more_seats = sorted(seats_by_party.items(), key=lambda kv: kv[1], reverse=True)[0]
        winner =  party_with_more_seats[0] if party_with_more_seats[1] >= 325 else "noone"
        
        is_shares_valid = sum(item["sum_share"] for item in party_results.values()) == 100

        total_shares_flat = sum(item.share for item in flat_results)
        return {
            **seats_by_party,
            "winner": winner,
            "sum": total_seats,
        }
