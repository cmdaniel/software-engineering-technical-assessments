from collections import Counter
from dataclasses import dataclass, field
from dataclasses import dataclass
from itertools import groupby
from typing import Any
from model.log import build_logger
from model.model import Constituency, FlatConstituency, Party, PartyResult, Scoreboard
from itertools import groupby

logger = build_logger(__name__)

MIN_VOTES_TO_WIN = 325


@dataclass(frozen=True)
class ConstituencyWithWinner(Constituency):

    @property
    def winner(self) -> Party:
        winner = max(self.party_results, key=lambda item: item.votes)
        return winner.party


@dataclass
class ContextResult:
    constituencies: list[ConstituencyWithWinner] = field(
        default_factory=list[ConstituencyWithWinner]
    )
    scoreboard: Scoreboard = field(default_factory=Scoreboard)
    flat_constituencies: list[FlatConstituency] = field(
        default_factory=list[FlatConstituency]
    )


def parse_constituencies(
    payload: str | list[dict[str, Any]],
) -> list[ConstituencyWithWinner]:
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


def compute_seats_per_party(context: ContextResult) -> ContextResult:
    context.scoreboard.party_seats = Counter(
        item.winner for item in context.constituencies
    )
    return context


def compute_overall_winner(context: ContextResult) -> ContextResult:
    party, seats = max(context.scoreboard.party_seats.items(), key=lambda item: item[1])
    context.scoreboard.overall_winner = (
        Party(party) if seats >= MIN_VOTES_TO_WIN else Party.noone
    )
    return context


def compute_seats_sum(context: ContextResult) -> ContextResult:
    context.scoreboard.check_seats_sum = sum(
        item[1] for item in context.scoreboard.party_seats.items()
    )
    return context


def flat_constituency(context: ContextResult) -> ContextResult:
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


def compute_public_result(context: ContextResult) -> ContextResult:
    sorted_flat_items = sorted(context.flat_constituencies, key=lambda item: item.party)
    grouped = groupby(sorted_flat_items, key=lambda item: item.party)
    total_votes = sum(item.votes for item in context.flat_constituencies)
    for party, group in grouped:
        votes_sum = sum(item.votes for item in group)
        context.scoreboard.bonus_party_result[party] = {
            "votes": votes_sum,
            "shares": round(votes_sum / total_votes * 100, 2),
        }
    return context
