from collections import Counter
from dataclasses import dataclass, field
from decimal import Decimal
from itertools import groupby
from typing import Any
from model.log import build_logger
from model.model import Constituency, FlatConstituency, Party, PartyResult, Scoreboard


logger = build_logger(__name__)


@dataclass(slots=True)
class ContextResult:
    constituencies: list[Constituency] = field(default_factory=list)
    scoreboard: Scoreboard = field(default_factory=Scoreboard)


def map_to_constituency(payload: list[dict[str, Any]]) -> list[Constituency]:
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


def compute_constituencies_winner(context: str | ContextResult) -> str | ContextResult:
    if isinstance(context, str):
        raise TypeError(context)
    try:
        constituencies_with_winners = [
            Constituency(
                id=constituency.id,
                name=constituency.name,
                seq_no=constituency.seq_no,
                party_results=constituency.party_results,
                winner_party=(
                    max(constituency.party_results, key=lambda item: item.votes).party
                    if constituency.party_results
                    else Party.NOONE
                ),
            )
            for constituency in context.constituencies
        ]

        context.constituencies = constituencies_with_winners
        return context
    except Exception as ex:
        logger.error(ex)
        return str(ex)


def compute_party_seats(context: str | ContextResult) -> str | ContextResult:
    if isinstance(context, str):
        raise TypeError(context)
    try:

        context.scoreboard.party_seats = dict(
            Counter(str(item.winner_party) for item in context.constituencies)
        )

        return context

    except Exception as ex:
        logger.error(ex)
        return str(ex)


def compute_overall_winner(context: str | ContextResult) -> str | ContextResult:
    if isinstance(context, str):
        raise TypeError(context)
    try:

        if not context.scoreboard.party_seats:
            context.scoreboard.overall_winner = Party.NOONE
            return context

        winner_key, winner_seats = max(
            context.scoreboard.party_seats.items(), key=lambda item: item[1]
        )

        is_tied = (
            sum(
                1
                for seats in context.scoreboard.party_seats.values()
                if seats == winner_seats
            )
            > 1
        )

        context.scoreboard.overall_winner = (
            Party.NOONE if is_tied or winner_seats < 325 else Party(winner_key)
        )

        return context

    except Exception as ex:
        logger.error(ex)
        return str(ex)


def compute_seats_sum(context: str | ContextResult) -> str | ContextResult:
    if isinstance(context, str):
        raise TypeError(context)
    try:

        context.scoreboard.seats_sum = sum(
            value for _, value in context.scoreboard.party_seats.items()
        )
        return context

    except Exception as ex:
        logger.error(ex)
        return str(ex)


def compute_parties_result(context: str | ContextResult) -> str | ContextResult:
    if isinstance(context, str):
        raise TypeError(context)
    try:

        flat_results: list[FlatConstituency] = [
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

        max_votes = sum(item.votes for item in flat_results)

        sorted_results = sorted(flat_results, key=lambda item: item.party)
        group = groupby(sorted_results, key=lambda item: item.party)
        context.scoreboard.party_result = {
            party: {
                "votes": party_votes,
                "share": Decimal(round((party_votes / max_votes * 100), 2)),
            }
            for party, party_group in group
            for party_votes in [sum(item.votes for item in party_group)]
        }
        return context

    except Exception as ex:
        logger.error(ex)
        return str(ex)
