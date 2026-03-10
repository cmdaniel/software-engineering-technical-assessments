# Election API Scoreboard Specs

## Requirement Summary

The API must expose `GET /scoreboard` to report the election state using first-past-the-post logic.

Expected scoreboard output:
- Seats won per party.
- Overall winner when a party reaches at least 325 seats.
- Bonus: total votes per party.
- Bonus: total vote share per party.

Domain rules:
- Each constituency contributes one seat.
- Constituency winner is the party with the highest vote count in that constituency.
- A party is the overall winner when seats >= 325.

## Implementation Logic (Scoreboard)

The current codebase has a scoreboard placeholder in `ResultsController.scoreboard()`.

Recommended implementation behavior:
1. Read all stored result entries from `ResultStore.get_all()`.
2. Aggregate results by constituency id.
3. For each constituency, select the party with the max `votes` and award one seat.
4. Aggregate total votes for each party across all results.
5. Compute vote share for each party from global total votes.
6. Derive overall winner when any party reaches 325 seats.
7. Return a JSON object with `seats`, `winner`, and (bonus) `votes` and `share` sections.

## Flow Diagram

```mermaid
flowchart TD
    A[GET /scoreboard request] --> B[ResultsController.scoreboard]
    B --> C[Fetch all results from ResultStore.get_all]
    C --> D{Any results loaded?}
    D -- No --> E[Return empty scoreboard with no winner]
    D -- Yes --> F[Group by constituency id]
    F --> G[For each constituency, find party with max votes]
    G --> H[Increment seat count for winning party]
    H --> I[Accumulate total votes for each party]
    I --> J[Compute vote share per party]
    J --> K{Any party seats >= 325?}
    K -- Yes --> L[Set overall winner to that party]
    K -- No --> M[Set overall winner to null]
    L --> N[Return scoreboard JSON]
    M --> N
```

## Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant S as Flask Server
    participant RC as ResultsController
    participant RS as ResultStore

    C->>S: GET /scoreboard
    S->>RC: scoreboard()
    RC->>RS: get_all()
    RS-->>RC: list[results]

    alt no results
        RC-->>S: {}
        S-->>C: 200 OK + {}
    else results available
        Note over RC: Build per-party seats by constituency winner
        Note over RC: Build per-party total votes and vote share
        Note over RC: Determine winner if seats >= 325
        RC-->>S: scoreboard payload
        S-->>C: 200 OK + scoreboard JSON
    end
```
