from collections import Counter
from model.log import build_logger
from model.model import Constituency, Party, PartyResult, Scoreboard
from results_service import ResultStore
from typing import Any, Callable
from dataclasses import dataclass, field

logger = build_logger(__name__)
logger.info("service started")


@dataclass(slots=True)
class ContextResult:
    constituencies: list[Constituency] = field(default_factory=list)
    scoreboard: Scoreboard = field(default_factory=Scoreboard)
    # flattened_items: list[FlatConstituency] = field(default_factory=list)
    # grouped_by_key: defaultdict[str, list[FlatConstituency]] = field(
    #     default_factory=lambda: defaultdict(list)
    # )
    # summary: dict[str, int] = field(default_factory=dict)


class ResultsController:
    def __init__(self) -> None:
        self.store: ResultStore = ResultStore()

    def get_result(self, id: int) -> str | dict:
        return self.store.get_result(id)

    def get_all(self) -> list[dict]:
        return self.store.get_all()

    def new_result(self, result: dict) -> dict:
        self.store.new_result(result)
        return {}

    def reset(self) -> None:
        self.store.reset()

    def pipe(self, value: Any, *functions: Callable[[Any], Any]) -> ContextResult:
        for function in functions:
            value = function(value)
        return value

    def map_to_constituency(self, payload: list[dict[str, Any]]) -> list[Constituency]:
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

    def load_data(self, context: str | ContextResult) -> str | ContextResult:
        if isinstance(context, str):
            raise TypeError(context)
        try:
            context.constituencies = self.map_to_constituency(self.get_all())
            return context
        except Exception as ex:
            logger.error(ex)
            return str(ex)

    def compute_constituencies_winner(
        self, context: str | ContextResult
    ) -> str | ContextResult:
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
                        max(
                            constituency.party_results, key=lambda item: item.votes
                        ).party
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

    def compute_party_seats(self, context: str | ContextResult) -> str | ContextResult:
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

    def compute_overall_winner(
        self, context: str | ContextResult
    ) -> str | ContextResult:
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

    def scoreboard(self) -> dict:
        try:
            logger.info("scoreboard started")
            pipe_run = self.pipe(
                ContextResult(),
                self.load_data,
                self.compute_constituencies_winner,
                self.compute_party_seats,
                self.compute_overall_winner,
            )

            if isinstance(pipe_run, str):
                raise TypeError(pipe_run)

            result = {**pipe_run.scoreboard.party_seats, Party.WINNER: pipe_run.scoreboard.overall_winner }
            # result = {Party.LD: 1, Party.LAB: 4, Party.WINNER: Party.NOONE}
            logger.info("scoreboard succesfully generated")
            return result
        except Exception as ex:
            logger.error(ex)

        return {}
