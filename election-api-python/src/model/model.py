from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum


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
    party_result: dict[Party, dict[str, int | Decimal]] = field(default_factory=dict)


@dataclass(slots=True)
class PartyResult:
    party: Party = Party.noone
    votes: int = 0
    share: Decimal = Decimal(0)


@dataclass(slots=True)
class Constituency:
    id: int = 0
    name: str = ""
    seq_no: int = 0
    winner: Party = Party.noone
    party_results: list[PartyResult] = field(default_factory=list)


@dataclass(slots=True)
class FlatConstituency:
    id: int = 0
    name: str = ""
    seq_no: int = 1
    party: Party = Party.noone
    votes: int = 0
    share: Decimal = Decimal(0)
