from abc import ABC, abstractmethod
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


class ScoreboardKey(StrEnum):
    winner = "winner"
    sum = "sum"


class PartyResultEnum(StrEnum):
    VOTES = "votes"
    SHARES = "shares"


@dataclass(frozen=True)
class PartyResult:
    party: Party = Party.noone
    votes: int = 0
    share: Decimal = Decimal(0)


@dataclass(frozen=True)
class Constituency(ABC):
    id: int = 0
    name: str = ""
    seq_no: int = 0
    party_results: list[PartyResult] = field(default_factory=list)

    @property
    @abstractmethod
    def winner(self) -> Party: ...


@dataclass(frozen=True)
class FlatConstituency:
    id: int = 0
    name: str = ""
    seq_no: int = 1
    party: Party = Party.noone
    votes: int = 0
    share: Decimal = Decimal(0)


@dataclass(slots=True)
class Scoreboard:
    party_seats: dict[str, int] = field(default_factory=dict)
    overall_winner: Party = Party.noone
    check_seats_sum: int = 0
    check_is_tied: bool = False
    bonus_party_result: list[PartyResult] = field(default_factory=list[PartyResult])
