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
    NOONE = "noone"
    WINNER = "winner"
    SUM = "sum"


class PartyResultEnum(StrEnum):
    VOTES = "votes"
    SHARES = "shares"


@dataclass(slots=True)
class Scoreboard:
    party_seats: dict[str, int] = field(default_factory=dict)
    overall_winner: Party = Party.NOONE
    party_result: dict[Party, dict[str, dict[Party, int | Decimal]]] = field(
        default_factory=dict
    )
    is_tied: bool = False


@dataclass(slots=True)
class PartyResult:
    party: Party = Party.NOONE
    votes: int = 0
    share: Decimal = Decimal(0)


@dataclass(slots=True)
class Constituency:
    id: int = 0
    name: str = ""
    seq_no: int = 0
    winner_party: Party = Party.NOONE
    party_results: list[PartyResult] = field(default_factory=list)


@dataclass(slots=True)
class FlatConstituency:
    id: int = 0
    name: str = ""
    seq_no: int = 1
    party: Party = Party.NOONE
    votes: int = 0
    share: Decimal = Decimal(0)
