from collections import Counter
from dataclasses import dataclass, field
from itertools import groupby
from typing import Any, Callable, Protocol

from model.log import build_logger
from model.model import Constituency, FlatConstituency, Party, PartyResult, Scoreboard


logger = build_logger(__name__)

SEATS_TO_WIN = 325


class WinnerPolicy(Protocol):
    def __call__(self, party_seats: dict[str, int]) -> Party: ...


class ConstituencyWithWinner(Constituency):

    @property
    def winner(self) -> Party:
        if not self.party_results:
            return Party.noone
        return max(self.party_results, key=lambda item: item.votes).party


@dataclass(slots=True)
class ContextResult:
    constituencies: list[ConstituencyWithWinner] = field(default_factory=list)
    scoreboard: Scoreboard = field(default_factory=Scoreboard)
    flat_constituencies: list[FlatConstituency] = field(default_factory=list)


def compute_party_seats(context: ContextResult) -> ContextResult:
    context.scoreboard.party_seats = dict(
        Counter(item.winner for item in context.constituencies)
    )
    return context


def plurality_winner(party_seats: dict[str, int]) -> Party:
    """First-past-the-post: party wins if it holds >= SEATS_TO_WIN seats."""
    if not party_seats:
        return Party.noone
    winner_party, seats = max(party_seats.items(), key=lambda item: item[1])
    return Party(winner_party) if seats >= SEATS_TO_WIN else Party.noone


def compute_overall_winner(
    context: ContextResult, policy: WinnerPolicy = plurality_winner
) -> ContextResult:
    context.scoreboard.winner = policy(context.scoreboard.party_seats)
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
        [item for item in context.constituencies if item.winner is not Party.noone]
    )
    total_votes = sum(item.votes for item in context.flat_constituencies)
    for key, group in groupby(flat_items, key=lambda item: item.party):
        sum_votes = sum(item.votes for item in group)
        context.scoreboard.party_result[key] = {
            "votes": sum_votes,
            "shares": round(sum_votes / total_votes * 100, 2),
        }
    return context


def parse_constituencies(payload: str | list[dict[str, Any]]) -> list[ConstituencyWithWinner]:
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
        logger.error("Failed to parse constituencies: %s", ex)
    return []
