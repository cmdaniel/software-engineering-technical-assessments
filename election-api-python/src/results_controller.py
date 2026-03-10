from results_service import ResultStore
from DM_policy_engine import FirstPastThePostPolicyEngine

class ResultsController:

    def __init__(self) -> None:
        self.result_store: ResultStore = ResultStore()
        self.policy_engine = FirstPastThePostPolicyEngine()

    def get_result(self, identifier: int) -> str | dict:
        return self.result_store.get_result(identifier)

    def new_result(self, result: dict) -> dict:
        self.result_store.new_result(result)
        return {}

    def reset(self) -> None:
        self.result_store.reset()

    def scoreboard(self) -> dict:
        parameters = self.policy_engine.build_parameters(self.result_store.get_all())
        return parameters.to_dict()
