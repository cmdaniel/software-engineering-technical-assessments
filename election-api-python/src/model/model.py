from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class PartyEnum(Enum):
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


class PartyResultEnum(Enum):
    VOTES = "votes"
    SHARES = "shares"


@dataclass
class Scoreboard:
    party_seats: dict[PartyEnum, int]
    overall_winner: PartyEnum
    party_result: dict[PartyEnum, dict[str, dict[PartyEnum, int | Decimal]]]
    is_tied: bool = False


@dataclass
class PartyResult:
    party: PartyEnum
    votes: int
    share: Decimal


@dataclass
class Constituency:
    id: int
    name: str
    seqNo: int
    PartyResults: list[PartyResult]


@dataclass
class FlatConstituency:
    id: int
    name: str
    seqNo: int
    party: PartyEnum
    votes: int
    share: Decimal
