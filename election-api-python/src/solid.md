# Top 5 Recommendations (priority order)

## Fix LSP — Replace raise NotImplementedError() in Constituency with ABC + @abstractmethod. This is a correctness issue, not just style.

## Fix DIP — Define a ResultRepository Protocol and inject it into ResultsController. This enables testability and future storage backends.

## Clean up domain.py — Remove plot_chart entirely (or move to a presentation module), deduplicate compute_scoreboard/compute_scoreboard_party_seats, and rename map_to_parents → parse_constituencies.

## Fix Party enum — Separate actual parties from metadata. Use a Scoreboard field or a dedicated ScoreboardKey sentinel enum for winner and sum.

## Extract a voting strategy — Wrap MIN_VOTES_TO_WIN in a callable/policy object so alternative systems (tasks.md bonus items) can be plugged in without touching compute_overall_winner.