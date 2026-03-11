from pandas.core.groupby import DataFrameGroupBy
from results_service import ResultStore
from dataclasses import dataclass
import pandas as pd

@dataclass
class PartyResult:
    party: str
    votes: int
    share: float

@dataclass
class ElectionResult:
    id: int
    name: str
    seqNo: int
    partyResults: list[PartyResult]

class ResultsController:

    def __init__(self) -> None:
        self.result_store: ResultStore = ResultStore()

    def get_result(self, identifier: int) -> str | dict:
        return self.result_store.get_result(identifier)

    def new_result(self, result: dict) -> dict:
        self.result_store.new_result(result)
        return {}
    
    def get_result_all(self) -> str | list[dict]:
        return self.result_store.get_all()

    def reset(self) -> None:
        self.result_store.reset()

    def exploded_normalised_results(self, result: list[ElectionResult]) -> None | pd.DataFrame:
        """
        Create a pandas dataframe from the result and performe 
        explode -> normalise -> groupby operations to get the 
        total votes for each party in the result
        """
        # Create a pandas dataframe from the result
        df = pd.DataFrame([r.__dict__ for r in result])
        # partyResults is an array of objects that we want to explode into separate rows, preserving the { id, name and seqNo }.
        df_exploded = df.explode("partyResults", ignore_index=True)
        # partyResults column is now a series of dictionaries we want to normalise into separate columns form party, votes and share.
        df_normalised = pd.json_normalize(df_exploded.pop("partyResults").tolist())
        df_exploded = pd.concat([df_exploded, df_normalised], axis=1)
        return df_exploded if len(df_exploded) > 0 else None
    
    def exploded_normalised_grouped_results(self, result: list[ElectionResult], group_by: str) -> None | DataFrameGroupBy:
        """
        Create a pandas datafram from the result and performe 
        explode -> normalise -> groupby operations to get the
        total votes for each party in the result
        """
        df_exploded_normalised = pd.DataFrame(self.exploded_normalised_results(result))
        df_grouped = df_exploded_normalised.groupby(group_by)
        return df_grouped if len(df_grouped) > 0 else None
    
    def scoreboard(self) -> dict:
        # Left blank for you to fill in
        # assert LD == 62
        # assert LAB == 349
        # assert CON == 210
        # assert winner = LAB
        # assert sum = 650
        dict_results = self.get_result_all()
        results = [ElectionResult(**r) for r in dict_results] if isinstance(dict_results, list) else []
        df_elt: None | DataFrameGroupBy = self.exploded_normalised_grouped_results(results, "id")
        
        # for each constituency (df_elt groups), get the party with the most votes and sum the total votes for each party across all constituencies.
        seats_by_parties = df_elt.apply(lambda group:  group.loc[group["votes"].idxmax()]["party"]).value_counts().to_dict() if df_elt is not None else {}
        max_seats_party = max(seats_by_parties, key=seats_by_parties.__getitem__) if len(seats_by_parties) > 0 else "noone"
        # Be careful, since it might be a tie!
        # check if there are multiple parties with the same number of seats as the max, if so, winner is noone, otherwise winner is the party with the most seats.
        max_seats = seats_by_parties[max_seats_party] if max_seats_party in seats_by_parties else 0
        is_tie = list(seats_by_parties.values()).count(max_seats) > 1
        winner = "noone" if is_tie else max_seats_party
        winner = max_seats_party if len(seats_by_parties) > 0 and seats_by_parties[max_seats_party] >= 325 else "noone"

        total_seats = sum(seats_by_parties.values())

        return { **seats_by_parties, "winner": winner, "sum": total_seats }
        # return {
        #     "LD": 1,
        #     "LAB": 4,
        #     "winner": "noone",
        # }
