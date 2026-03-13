from dataclasses import dataclass
from enum import StrEnum

MIN_VOTES = 325


@dataclass()
class PartyResult:
    party: str = "noone"
    votes: int = 0
    share: int = 0


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


class Party(StrEnum):
    LD = "LD"
    LAB = "LAB"
    CON = "CON"
    WINNER = "WINNER"
    SUM = "SUM"


def map_results(raw_items: list[dict]) -> list[Result]:
    mapped_items = (
        [
            Result(
                id=item["id"],
                name=item["name"],
                seqNo=item["seqNo"],
                partyResults=[
                    PartyResult(**subitem) for subitem in item.get("partyResults", [])
                ],
            )
            for item in raw_items
        ]
        if isinstance(raw_items, list)
        else []
    )
    return mapped_items


def flat_result(mapped_result: list[Result]):
    flat_results: list[FlatResult] = [
        FlatResult(
            id=parent.id,
            name=parent.name,
            seqNo=parent.seqNo,
            party=child.party,
            votes=child.votes,
            share=child.share,
            seat_winner_party=max(
                parent.partyResults, key=lambda item: item.votes, default=PartyResult
            ).party,
        )
        for parent in mapped_result
        for child in parent.partyResults
    ]
    return flat_results
