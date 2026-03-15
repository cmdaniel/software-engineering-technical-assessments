from dataclasses import dataclass
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


@dataclass
class Scoreboard:
    party_seats: dict[Party, int]
    overall_winner: Party
    party_result: dict[Party, dict[str, dict[Party, int | Decimal]]]
    is_tied: bool = False


@dataclass
class PartyResult:
    party: Party
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
    party: Party
    votes: int
    share: Decimal
