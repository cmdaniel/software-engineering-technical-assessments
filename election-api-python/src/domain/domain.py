from dataclasses import dataclass, field
from collections import Counter
from model.log import logger
from model.model import Constituency, FlatConstituency, PartyResult, Scoreboard
from typing import Any


@dataclass(slots=True)
class ContextResult:
    constituencies: list[Constituency] = field(default_factory=list[Constituency])
    scoreboard: Scoreboard = field(default_factory=Scoreboard)
    flat_constituencies: list[FlatConstituency] = field(
        default_factory=list[FlatConstituency]
    )


def map_constituencies(payload: str | list[dict[str, Any]]) -> list[Constituency]:
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
        logger.error(error_msg)

    return []


def transform_flat_constituencies(context: ContextResult) -> ContextResult:
    context.flat_constituencies = [
        FlatConstituency(
            id=parent.id,
            name=parent.name,
            seq_no=parent.seq_no,
            party=child.party,
            votes=child.votes,
            share=child.share,
        )
        for parent in context.constituencies
        for child in parent.party_results
    ]
    return context


def compute_constituency_winner(context: ContextResult) -> ContextResult:

    for constituency in context.constituencies:
        constituency.winner_party = max(
            constituency.party_results, key=lambda item: item.votes
        ).party

    return context


def compute_party_seats(context: ContextResult) -> ContextResult:

    context.scoreboard.party_seats = dict(
        Counter(constituency.winner_party for constituency in context.constituencies)
    )

    return context


