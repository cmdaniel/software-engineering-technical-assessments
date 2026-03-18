from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum
from functools import cached_property


class Party(StrEnum):
    LAB = "LAB"
    CON = "CON"
    LD = "LD"
    PC = "PC"
    OTH = "OTH"
    GRN = "GRN"
    UKIP = "UKIP"
    noone = "noone"
    winner = "winner"
    sum = "sum"


class PartyResultEnum(StrEnum):
    VOTES = "votes"
    SHARES = "shares"


@dataclass(slots=True)
class Scoreboard:
    party_seats: dict[str, int] = field(default_factory=dict)
    winner: Party = Party.noone
    seats_sum: int = 0
    is_tied: bool = False
    party_result: dict[Party, dict[str, int | float]] = field(default_factory=dict)


@dataclass(frozen=True)
class PartyResult:
    party: Party = Party.noone
    votes: int = 0
    share: Decimal = Decimal(0)


@dataclass(frozen=True)
class Constituency:
    id: int = 0
    name: str = ""
    seq_no: int = 0
    party_results: list[PartyResult] = field(default_factory=list)

    @cached_property
    def _winner(self) -> Party:
        raise NotImplementedError()

    def winner(self) -> Party:
        raise NotImplementedError()


@dataclass(frozen=True)
class FlatConstituency:
    id: int = 0
    name: str = ""
    seq_no: int = 1
    party: Party = Party.noone
    votes: int = 0
    share: Decimal = Decimal(0)
