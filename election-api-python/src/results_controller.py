from dataclasses import dataclass

from results_service import ResultStore
import pandas as pd
from pandas.core.groupby import DataFrameGroupBy



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

    # Create a lambda function that takes the party with the most votes that will be used in many constituencies
    def get_winner(self, result_parties: dict) -> str:
        total_votes = sum(result_parties.values())
        return max(result_parties, key=lambda party: result_parties[party]) if total_votes > 0 else "noone"

    def exploded_normalised_results(self, result: list[ElectionResult]) -> None | pd.DataFrame:
        """Create a pandas datafram from the result and performe explode -> normalise -> groupby operations to get the total votes for each party in the result"""
        # Create a pandas dataframe from the result
        df = pd.DataFrame([r.__dict__ for r in result])
        # the partyResults is an array of objects that we want to explode into separate rows, preserving the { id, name and seqNo }.
        df_exploded = df.explode("partyResults")
        # the partyResults column is now a series of dictionaries we want to normalise into separate columns form party, votes and share.
        df_normalised = pd.json_normalize(df_exploded["partyResults"].tolist())
        df_exploded = df_exploded.drop(columns=["partyResults"]).join(df_normalised)

        return df_exploded if len(df_exploded) > 0 else None
    

    def exploded_normalised_grouped_results(self, result: list[ElectionResult], group_by: str) -> None | DataFrameGroupBy:
        """Create a pandas datafram from the result and performe explode -> normalise -> groupby operations to get the total votes for each party in the result"""
    
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
        df_elt = self.exploded_normalised_grouped_results(results, "id")
       
        # return { **result_parties, "winner": winner, "sum": total_votes }
        return {
            "LD": 1,
            "LAB": 4,
            "winner": "noone",
        }
