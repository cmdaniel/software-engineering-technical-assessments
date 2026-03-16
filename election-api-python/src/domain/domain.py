import matplotlib.pyplot as plt
from collections import Counter
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any
from model.log import build_logger
from model.model import Constituency, FlatConstituency, Party, PartyResult, Scoreboard
from itertools import groupby

logger = build_logger(__name__)
logger.info("service started")

MIN_VOTES_TO_WIN = 325


@dataclass(slots=True)
class ContextResult:
    constituences: list[Constituency] = field(default_factory=list)
    flat_constituency: list[FlatConstituency] = field(default_factory=list)
    scoreboard: Scoreboard = field(default_factory=Scoreboard)


def map_to_parents(payload: str | list[dict[str, Any]]) -> list[Constituency]:
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


def flat_constituency(context: ContextResult) -> ContextResult:
    context.flat_constituency = [
        FlatConstituency(
            id=parent.id,
            name=parent.name,
            seq_no=parent.seq_no,
            party=child.party,
            votes=child.votes,
            share=child.share,
        )
        for parent in context.constituences
        for child in parent.party_results
    ]
    return context


def compute_constituency_winner(context: ContextResult) -> ContextResult:

    for constituency in context.constituences:
        constituency.winner = max(
            constituency.party_results, key=lambda item: item.votes
        ).party

    context.scoreboard.party_seats = Counter(
        constituency.winner for constituency in context.constituences
    )
    return context


def compute_overall_winner(context: ContextResult) -> ContextResult:
    winner, votes = max(
        context.scoreboard.party_seats.items(), key=lambda item: item[1]
    )
    context.scoreboard.winner = (
        Party(winner) if votes >= MIN_VOTES_TO_WIN else Party.noone
    )
    return context


def compute_seats_sum(context: ContextResult) -> ContextResult:

    context.scoreboard.seats_sum = sum(
        item[1] for item in context.scoreboard.party_seats.items()
    )
    return context


def compute_is_tied(context: ContextResult) -> ContextResult:
    winner_votes = context.scoreboard.party_seats[context.scoreboard.winner]
    seats_same_as_winner = list(
        filter(lambda item: item[1] == winner_votes, context.scoreboard.party_seats)
    )
    context.scoreboard.is_tied = len(seats_same_as_winner) > 1
    return context


def plot_chart(context: ContextResult) -> ContextResult:
    try:
        data: dict[str, int] = {
            k: int(v["votes"])
            for k, v in context.scoreboard.party_result.items()
            if int(v["votes"]) > 1000000
        }

        labels = list(data.keys())
        sizes = list(data.values())

        plt.figure(figsize=(6, 6))
        plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
        plt.title("Pie Chart")
        plt.axis("equal")
        plt.tight_layout()
        plt.show()
    except Exception as ex:
        print(ex)

    return context


def compute_public_party_result(context: ContextResult) -> ContextResult:

    flat_items = sorted(context.flat_constituency, key=lambda item: item.party)

    grouped = {
        key: sum(item.votes for item in group)
        for key, group in groupby(flat_items, key=lambda item: item.party)
    }

    total_votes = sum(item.votes for item in context.flat_constituency)

    for party, votes in grouped.items():
        context.scoreboard.party_result[party] = {
            "votes": votes,
            "share": Decimal(round(votes / total_votes * 100, 2)),
        }

    return context
