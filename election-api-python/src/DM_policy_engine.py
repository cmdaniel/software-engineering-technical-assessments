from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ElectionPolicyConfig:
    """Configuration inputs used by policy/business rules."""

    majority_seat_threshold: int = 325


@dataclass(frozen=True)
class ScoreboardParameters:
    """Normalized policy-ready values derived from raw election results."""

    seats_by_party: dict[str, int]
    votes_by_party: dict[str, int]
    vote_share_by_party: dict[str, float]
    declared_constituencies: int
    total_votes_cast: int
    winner: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "seats": self.seats_by_party,
            "votes": self.votes_by_party,
            "voteShare": self.vote_share_by_party,
            "declaredConstituencies": self.declared_constituencies,
            "totalVotesCast": self.total_votes_cast,
            "winner": self.winner,
        }


class FirstPastThePostPolicyEngine:
    """Transforms election result rows into data consumable by business rules."""

    def __init__(self, config: ElectionPolicyConfig | None = None) -> None:
        self.config = config or ElectionPolicyConfig()

    def build_parameters(self, constituency_results: list[dict[str, Any]]) -> ScoreboardParameters:
        seats_by_party: dict[str, int] = {}
        votes_by_party: dict[str, int] = {}

        for constituency in constituency_results:
            party_results = constituency.get("partyResults", [])
            if not party_results:
                continue

            winning_party = self._winning_party(party_results)
            if winning_party is not None:
                seats_by_party[winning_party] = seats_by_party.get(winning_party, 0) + 1

            for party_result in party_results:
                party = str(party_result.get("party", ""))
                votes = int(party_result.get("votes", 0))
                if not party:
                    continue
                votes_by_party[party] = votes_by_party.get(party, 0) + votes

        total_votes_cast = sum(votes_by_party.values())
        vote_share_by_party = self._vote_share(votes_by_party, total_votes_cast)

        return ScoreboardParameters(
            seats_by_party=seats_by_party,
            votes_by_party=votes_by_party,
            vote_share_by_party=vote_share_by_party,
            declared_constituencies=sum(seats_by_party.values()),
            total_votes_cast=total_votes_cast,
            winner=self._overall_winner(seats_by_party),
        )

    def _winning_party(self, party_results: list[dict[str, Any]]) -> str | None:
        # If two parties tie with the highest vote total, the constituency has no declared winner.
        sorted_results = sorted(
            party_results,
            key=lambda row: int(row.get("votes", 0)),
            reverse=True,
        )
        if not sorted_results:
            return None

        top_votes = int(sorted_results[0].get("votes", 0))
        winners = [row for row in sorted_results if int(row.get("votes", 0)) == top_votes]
        if len(winners) != 1:
            return None

        party = winners[0].get("party")
        return str(party) if party else None

    def _overall_winner(self, seats_by_party: dict[str, int]) -> str | None:
        for party, seats in seats_by_party.items():
            if seats >= self.config.majority_seat_threshold:
                return party
        return None

    def _vote_share(self, votes_by_party: dict[str, int], total_votes_cast: int) -> dict[str, float]:
        if total_votes_cast == 0:
            return {party: 0.0 for party in votes_by_party}

        return {
            party: round((votes / total_votes_cast) * 100, 2)
            for party, votes in votes_by_party.items()
        }
