from collections import Counter
from dataclasses import dataclass, field
from dataclasses import dataclass
from typing import Any
from model.model import Constituency, Party, PartyResult, Scoreboard


@dataclass
class ContextResult:
    constituences: list[Constituency] = field(default_factory=list[Constituency])
    scoreboard: Scoreboard = field(default_factory= Scoreboard)


def compute_constituency_winner(context: ContextResult) -> ContextResult:
    for constituency in context.constituences:
        list_winner = max(constituency.party_results, key=lambda item: item.votes)
        constituency.winner = list_winner.party
    return context


def compute_seats_winner(context: ContextResult) -> ContextResult:
    context.scoreboard.party_seats = dict(Counter(item.winner for item in context.constituences))
    return context


def flat_constituency(context: ContextResult) -> ContextResult:
    return context


def compute_overall_winner(context: ContextResult) -> ContextResult:
    return context


def map_to_parents(payload: list[dict[str, Any]]) -> list[Constituency]:
    try:
        if isinstance(payload, str):
            raise TypeError(payload)

        return [
            Constituency(
                id=parent["id"],
                name=parent["name"],
                seq_no=parent["seqNo"],
                party_results=[
                    PartyResult(
                        party=child["party"],
                        votes=child["votes"],
                        share=child["share"],
                    )
                    for child in parent["partyResults"]
                ],
            )
            for parent in payload
        ]

    except (AttributeError, KeyError, TypeError) as ex:
        error_msg = f"{ex}"
        # logger.error(error_msg)

    return []
