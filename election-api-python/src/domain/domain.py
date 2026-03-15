from dataclasses import dataclass
from model.log import logger
from model.model import Constituency, PartyResult, Scoreboard
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ContextResult:
    constituencies: list[Constituency] = []
    scoreboard: Scoreboard = Scoreboard()


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