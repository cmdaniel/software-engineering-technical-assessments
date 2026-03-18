from typing import Protocol


class ResultRepository(Protocol):
    def get_result(self, result_id: int) -> dict | None: ...
    def new_result(self, result: dict) -> None: ...
    def get_all(self) -> list[dict]: ...
    def reset(self) -> None: ...


class ResultStore:

    def __init__(self) -> None:
        self.store: list[dict] = []

    def get_result(self, result_id: int) -> dict | None:
        results = [r for r in self.store if r['id'] == result_id]
        return results[0] if results else None

    def new_result(self, result: dict) -> None:
        self.store.append(result)

    def get_all(self) -> list[dict]:
        return self.store

    def reset(self) -> None:
        self.store = []