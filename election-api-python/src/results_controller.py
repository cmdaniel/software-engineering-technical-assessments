from dataclasses import dataclass
from results_service import ResultStore
from model import Party, MIN_VOTES
from collections import defaultdict

@dataclass()
class PartyResult:
    party: str
    votes: int
    share: int


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
    seat_winner_party: str


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
        mapped_items = self.map_results(raw_items)
        return mapped_items

    def reset(self) -> None:
        self.store.reset()

    def map_results(self, results: list[dict]) -> list[Result]:
        mapped_items = (
            [
                Result(
                    id=item["id"],
                    name=item["name"],
                    seqNo=item["seqNo"],
                    partyResults=[
                        PartyResult(**subitem)
                        for subitem in item.get("partyResults", [])
                    ],
                )
                for item in results
            ]
            if isinstance(results, list)
            else []
        )
        return mapped_items

    def flat_results(self, results: list[Result]) -> list[FlatResult]:
        flat_results: list[FlatResult] = [
            FlatResult(
                id=parent.id,
                name=parent.name,
                seqNo=parent.seqNo,
                party=child.party,
                votes=child.votes,
                share=child.share,
                seat_winner_party=max(
                    parent.partyResults,
                    key=lambda item: item.votes,
                    default=PartyResult(party="noone", votes=0, share=0),
                ).party,
            )
            for parent in results
            for child in parent.partyResults
        ]
        return flat_results

    def scoreboard(self) -> dict:
        try:
            payload = self.get_all()

            if not payload or isinstance(payload, str):
                raise AppValidationError("payload is required")

            flat_results = self.flat_results(payload)

            grouped = defaultdict(list)
            for item in flat_results:
                if item.seat_winner_party == item.party:
                    grouped[item.party].append(item)

            result_dict = {party: len(seats) for party, seats in grouped.items()}
            top_party, top_seats = max(
                result_dict.items(), key=lambda item: item[1], default=("noone", 0)
            )

            is_tied = list(result_dict.values()).count(top_seats) > 1

            winner = top_party if top_seats >= MIN_VOTES and not is_tied else "noone"

            total_votes = sum(result_dict.values())

            return {**result_dict, Party.WINNER: winner, Party.SUM: total_votes}

        except AttributeError as err:
            print(err)
            pass
        except Exception as err:
            print(err)
            pass
        finally:
            self.reset()

        return {}
