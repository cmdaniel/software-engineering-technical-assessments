from dataclasses import dataclass

from results_service import ResultStore
from model import Party


@dataclass()
class PartyResult:
    party: str
    votes: int
    share: float


@dataclass()
class Result:
    id: int
    name: str
    seqNo: int
    partyResults: list[PartyResult]


@dataclass()
class FlatResult:
    id: int
    name: str
    seqNo: int
    party: str
    votes: int
    share: int


class DataLoadingError(Exception):
    """Raised when data loading fails."""


class ResultsController:
    def __init__(self) -> None:
        self.result_store: ResultStore = ResultStore()

    def get_result(self, identifier: int) -> str | dict:
        return self.result_store.get_result(identifier)

    def new_result(self, result: dict) -> dict:
        self.result_store.new_result(result)
        return {}

    def get_all(self) -> str | list[Result]:
        results = self.result_store.get_all()
        mapped_items = [self._map_result(item) for item in results] if isinstance(results, list) else []
        return mapped_items

    def reset(self) -> None:
        self.result_store.reset()

    def scoreboard(self) -> dict:
        try:
            results: str | list[Result] = self.get_all()

            if not isinstance(results, list):
                raise DataLoadingError("Data Loading error on scoreboard")

            seats_by_party: dict[str, int] = {}
            for result in results:
                if not result.partyResults:
                    continue

                constituency_winner = max(
                    result.partyResults,
                    key=lambda party_result: party_result.votes,
                )
                seats_by_party[constituency_winner.party] = (
                    seats_by_party.get(constituency_winner.party, 0) + 1
                )

            overall_winner = next(
                (
                    party
                    for party, seats in seats_by_party.items()
                    if seats >= 325
                ),
                "noone",
            )

            return {
                **seats_by_party,
                Party.WINNER: overall_winner,
            }

        except DataLoadingError as ex:
            print(ex)
            pass
        except AttributeError as ex:
            print(ex)
            pass
        except Exception as ex:
            print(ex)
            pass

        return {}

    def _map_result(self, item: dict | Result) -> Result:
        if isinstance(item, Result):
            return item

        return Result(
            id=item["id"],
            name=item["name"],
            seqNo=item["seqNo"],
            partyResults=[
                self._map_party_result(party_result)
                for party_result in item.get("partyResults", [])
            ],
        )

    def _map_party_result(self, item: dict | PartyResult) -> PartyResult:
        if isinstance(item, PartyResult):
            return item

        return PartyResult(
            party=item["party"],
            votes=item["votes"],
            share=item["share"],
        )
