from venv import logger


class ResultStore:
    def __init__(self) -> None:
        self.store: list[dict] = []

    def get_result(self, id_to_get) -> str | dict:
        result: list[dict] = list(
            filter(lambda result: result["id"] == int(id_to_get), self.store)
        )
        return f"No result with id {id_to_get} found." if len(result) < 1 else result[0]

    def new_result(self, result) -> None:
        self.store.append(result)

    def get_all(self) -> list[dict]:
        try:
            return self.store
        except Exception as ex:
            logger.error(ex)

        return []

    def reset(self) -> None:
        self.store: list[dict] = []
