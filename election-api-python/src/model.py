from enum import StrEnum

MIN_VOTES = 325

class Party(StrEnum):
    """Docstring for Party."""

    LD = "LD"
    LAB = "LAB"
    CON = "CON"
    WINNER = "WINNER"
    SUM = "SUM"
