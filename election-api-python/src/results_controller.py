from results_service import ResultStore
from model import Party


@c

class ResultsController:

    def __init__(self) -> None:
        self.store: ResultStore = ResultStore()

    def get_result(self, identifier: int) -> str | dict:
        return self.store.get_result(identifier)

    def new_result(self, result: dict) -> dict:
        self.store.new_result(result)
        return {}

    def reset(self) -> None:
        self.store.reset()

    def scoreboard(self) -> dict:
        
        
        
        return {Party.LD: 1, Party.LAB: 4, Party.WINNER: "noone"}
