from dataclasses import dataclass, field
from collections import Counter
from decimal import Decimal
from itertools import groupby
from model.log import logger
from model.model import Constituency, FlatConstituency, Party, PartyResult, Scoreboard
from typing import Any

MIN_VOTES_TO_WIN = 325


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
        constituency.winner = max(
            constituency.party_results, key=lambda item: item.votes
        ).party

    return context


def compute_party_seats(context: ContextResult) -> ContextResult:

    context.scoreboard.party_seats = dict(
        Counter(constituency.winner for constituency in context.constituencies)
    )

    return context


def compute_overall_winner(context: ContextResult) -> ContextResult:

    winner, votes = max(
        context.scoreboard.party_seats.items(), key=lambda item: item[1]
    )
    context.scoreboard.winner = (
        Party(winner) if votes >= MIN_VOTES_TO_WIN else Party.noone
    )

    parties_with_same_votes_as_winner = list(
        filter(
            lambda item: item[1] == votes,
            context.scoreboard.party_seats.items(),
        )
    )
    context.scoreboard.is_tied = len(parties_with_same_votes_as_winner) > 1

    return context


def compute_public_result(context: ContextResult) -> ContextResult:

    flat_items = sorted(context.flat_constituencies, key=lambda item: item.party)
    total_votes = sum(item.votes for item in context.flat_constituencies)

    context.scoreboard.party_result = {
        key: {
            "votes": sum(item.votes for item in group),
            "share": Decimal(
                round(sum(item.votes for item in group) / total_votes * 100, 2)
            ),
        }
        for key, group in groupby(flat_items, key=lambda item: item.party)
    }

    return context
