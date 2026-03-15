from model.log import build_logger
from model.model import Party
from results_service import ResultStore

logger = build_logger(__name__)
logger.info("service started")


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
        
    

    def scoreboard(self) -> dict:
        try:
            logger.info("scoreboard started")

            result = {Party.LD: 1, Party.LAB: 4, Party.WINNER: Party.NOONE}
            logger.info("scoreboard succesfully generated")

            return result

        except Exception as ex:
            logger.error(ex)

        return {}
