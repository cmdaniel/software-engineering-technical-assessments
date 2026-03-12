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

    def exploded_normalised_results(
        self, result: list[dict] | str
    ) -> None | pd.DataFrame:
        """
        Create a pandas dataframe from the result and performe
        explode -> normalise -> groupby operations to get the
        total votes for each party in the result
        """
        # Create a pandas dataframe from the result
        df = pd.DataFrame(result) if isinstance(result, list) else pd.DataFrame()
        # partyResults is an array of objects that we want to explode into separate rows, preserving the { id, name and seqNo }.
        df_exploded = df.explode("partyResults", ignore_index=True)
        # partyResults column is now a series of dictionaries we want to normalise into separate columns form party, votes and share.
        df_normalised = pd.json_normalize(df_exploded.pop("partyResults").tolist())
        df_exploded = pd.concat([df_exploded, df_normalised], axis=1)
        return df_exploded if len(df_exploded) > 0 else None

    def exploded_normalised_grouped_results(
        self, result: list[dict] | str, group_by: str
    ) -> None | DataFrameGroupBy:
        """
        Create a pandas datafram from the result and performe
        explode -> normalise -> groupby operations to get the
        total votes for each party in the result
        """
        df_exploded_normalised = pd.DataFrame(self.exploded_normalised_results(result))
        df_grouped = df_exploded_normalised.groupby(group_by)
        return df_grouped if len(df_grouped) > 0 else None

    def transform(self, result: list[dict] | str) -> None | pd.DataFrame:
        """
        Create a pandas dataframe from the result and performe
        explode -> normalise operations to get the total votes for each party in the result
        """
        df_exploded_normalised = pd.DataFrame(self.exploded_normalised_results(result))
        return df_exploded_normalised if len(df_exploded_normalised) > 0 else None

    def group_by_party(self, result: list[dict] | str) -> None | DataFrameGroupBy:
        """
        Create a pandas dataframe from the result and performe
        explode -> normalise -> groupby operations to get the total votes for each party in the result
        """
        df_exploded_normalised = pd.DataFrame(self.exploded_normalised_results(result))
        df_grouped = df_exploded_normalised.groupby("party")
        return df_grouped if len(df_grouped) > 0 else None

    def reducer_seats_by_party(self, result: list[dict] | str) -> dict:
        try:
            df_exploded_normalised = self.exploded_normalised_results(result)
            if df_exploded_normalised is None:
                return {}
            grouped_by_constituency = df_exploded_normalised.groupby("id")
            winning_parties = grouped_by_constituency.apply(
                lambda group: group.loc[group["votes"].idxmax(), "party"]
            )
            seats_by_party = winning_parties.value_counts().to_dict()
            return seats_by_party
        except KeyError as ex:
            print(f"Key error: {ex}")
            return {}

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
