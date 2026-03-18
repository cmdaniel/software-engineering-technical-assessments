from dataclasses import dataclass, field
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Counter
from model.log import build_logger
from model.model import Constituency, FlatConstituency, Party, PartyResult, Scoreboard
from itertools import groupby
import matplotlib.pyplot as plt


logger = build_logger(__name__)
logger.info("service started")

MIN_VOTES_TO_WIN = 325


class ConstituencyWithWinner(Constituency):
    
    @cached_property
    def _winner(self) -> Party:
        if not self.party_results:
            return Party.noone
        return max(self.party_results, key=lambda item: item.votes).party

    def winner(self) -> Party:
        return self._winner


@dataclass(slots=True)
class ContextResult:
    constituencies: list[ConstituencyWithWinner] = field(
        default_factory=list[ConstituencyWithWinner]
    )
    scoreboard: Scoreboard = field(default_factory=Scoreboard)
    flat_constituencies: list[FlatConstituency] = field(
        default_factory=list[FlatConstituency]
    )


# def compute_constituency_winners(context: ContextResult) -> ContextResult:
#     for constituency in context.constituencies:
#         constituency.winner = max(
#             constituency.party_results, key=lambda item: item.votes
#         ).party
#     return context


def compute_scoreboard(context: ContextResult) -> ContextResult:
    context.scoreboard.party_seats = dict(
        Counter(item.winner() for item in context.constituencies)
    )
    return context


def compute_scoreboard_party_seats(context: ContextResult) -> ContextResult:
    context.scoreboard.party_seats = dict(
        Counter(item.winner() for item in context.constituencies)
    )
    return context


def compute_overall_winner(context: ContextResult) -> ContextResult:
    try:
        winner = max(context.scoreboard.party_seats.items(), key=lambda item: item[1])
        context.scoreboard.winner = (
            Party(winner[0]) if int(winner[1]) >= MIN_VOTES_TO_WIN else Party.noone
        )
    except Exception as ex:
        print(ex)
    return context


def flat_constituencies(context: ContextResult) -> ContextResult:
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


def compute_party_results(context: ContextResult) -> ContextResult:
    flat_items = sorted(context.flat_constituencies, key=lambda item: item.party)
    context.scoreboard.seats_sum = len(
        [item for item in context.constituencies if item.winner() is not Party.noone]
    )
    total_votes = sum(item.votes for item in context.flat_constituencies)
    for key, group in groupby(flat_items, key=lambda item: item.party):
        sum_votes = sum(item.votes for item in group)
        context.scoreboard.party_result[key] = {
            "votes": sum_votes,
            "shares": round(sum_votes / total_votes * 100, 2),
        }
    return context


def compute_seats_sum(context: ContextResult) -> ContextResult:
    flat_items = sorted(context.flat_constituencies, key=lambda item: item.party)
    context.scoreboard.seats_sum = len(
        [item for item in context.constituencies if item.winner() is not Party.noone]
    )
    context.scoreboard.party_seats = {
        key: sum(item.votes for item in group)
        for key, group in groupby(flat_items, key=lambda item: item.party)
    }
    return context


def map_to_parents(payload: str | list[dict[str, Any]]) -> list[ConstituencyWithWinner]:
    try:
        if isinstance(payload, str):
            raise TypeError(payload)
        return [
            ConstituencyWithWinner(
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


def plot_chart(context: ContextResult) -> ContextResult:
    filtered = [
        item for item in context.scoreboard.party_seats.items() if item[1] >= 10
    ]
    data: dict[str, int] = dict(filtered)
    labels = list(data.keys())
    sizes = list(data.values())
    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
    plt.title("Pie Chart")
    plt.axis("equal")
    plt.tight_layout()
    plt.show()
    return context
