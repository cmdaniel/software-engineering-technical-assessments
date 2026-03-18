from model.log import build_logger
from results_service import ResultStore

# DM 
logger = build_logger(__name__)

class ResultsController:

    def __init__(self) -> None:
        self.store: ResultStore = ResultStore()
    
    def get_result(self, id: int) -> str | dict:
        return self.store.get_result(id)
    
    def new_result(self, result: dict) -> dict:
        self.store.new_result(result)
        return {}
    
    def reset(self) -> None:
        self.store.reset()
    
    # DM 
    def get_all(self) -> list[dict]:
        return self.store.get_all()
    
    def scoreboard(self) -> dict:
        # Left blank for you to fill in
        return {}
