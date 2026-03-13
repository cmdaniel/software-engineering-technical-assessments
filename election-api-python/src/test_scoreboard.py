import unittest
import json
import os
from werkzeug.test import TestResponse
from server import app, controller
from model import Party


class TestScoreboard(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.server = app.test_client(use_cookies=True)
        file_dir: str = os.path.dirname(os.path.realpath(__file__))
        self.RESULT_SAMPLE_PATH: str = f"{file_dir}/resources/sample-election-results"

    def load_and_post_result_file(self, num: int) -> TestResponse:
        file_number: str = str(num).zfill(3)
        with open(
            f"{self.RESULT_SAMPLE_PATH}/result{file_number}.json", "r", encoding="utf-8"
        ) as file:
            result = file.read()
        return self.server.post("/result", json=json.loads(result))

    def load_results(self, quantity: int) -> list[dict]:
        results = []
        for i in range(quantity):
            results.append(self.load_and_post_result_file(i + 1))
        return results

    def fetch_scoreboard(
        self,
    ) -> tuple[int, dict]:  # returns (status_code, response_body_object)
        response = self.server.get("/scoreboard")
        return (response.status_code, json.loads(response.data.decode("utf-8")))

    def setUp(self) -> None:
        controller.reset()

    def test_first_5(self) -> None:
        """
        # assert LD == 1
        # assert LAB = 4
        # assert winner = noone
        """
        self.load_results(5)
        status_code, scoreboard = self.fetch_scoreboard()

        self.assertEqual(
            status_code, 200, f"non-200 status code received: {status_code}"
        )
        self.assertNotEqual(len(scoreboard), 0)

        self.assertEqual(
            scoreboard[Party.LD], 1, f"{scoreboard[Party.LD]} should be equal to 1"
        )
        self.assertEqual(
            scoreboard[Party.LAB], 4, f"{scoreboard[Party.LAB]} should be equal to 4"
        )
        self.assertEqual(
            scoreboard[Party.WINNER],
            "noone",
            f"{scoreboard[Party.WINNER]} should be equal to noone",
        )

    def test_first_100(self) -> None:
        self.load_results(100)
        status_code, scoreboard = self.fetch_scoreboard()

        self.assertEqual(
            status_code, 200, f"non-200 status code received: {status_code}"
        )
        self.assertNotEqual(len(scoreboard), 0)
        self.assertEqual(
            scoreboard[Party.LD], 12, f"{scoreboard[Party.LD]} should be equal to 12"
        )
        self.assertEqual(
            scoreboard[Party.LAB], 56, f"{scoreboard[Party.LAB]} should be equal to 56"
        )
        self.assertEqual(
            scoreboard[Party.CON], 31, f"{scoreboard[Party.CON]} should be equal to 31"
        )
        self.assertEqual(
            scoreboard[Party.WINNER],
            "noone",
            f"{scoreboard[Party.WINNER]} should be equal to noone",
        )

    def test_first_554(self) -> None:
        self.load_results(554)
        status_code, scoreboard = self.fetch_scoreboard()

        self.assertEqual(
            status_code, 200, f"non-200 status code received: {status_code}"
        )
        self.assertNotEqual(len(scoreboard), 0)
        self.assertEqual(
            scoreboard[Party.LD], 52, f"{scoreboard[Party.LD]} should be equal to 52"
        )
        self.assertEqual(
            scoreboard[Party.LAB],
            325,
            f"{scoreboard[Party.LAB]} should be equal to 325",
        )
        self.assertEqual(
            scoreboard[Party.CON],
            167,
            f"{scoreboard[Party.CON]} should be equal to 167",
        )
        self.assertEqual(
            scoreboard[Party.WINNER],
            "LAB",
            f"{scoreboard[Party.WINNER]} should be equal to LAB",
        )

    def test_all_results(self) -> None:
        self.load_results(650)
        status_code, scoreboard = self.fetch_scoreboard()

        self.assertEqual(
            status_code, 200, f"non-200 status code received: {status_code}"
        )
        self.assertNotEqual(len(scoreboard), 0)
        self.assertEqual(
            scoreboard[Party.LD], 62, f"{scoreboard[Party.LD]} should be equal to 62"
        )
        self.assertEqual(
            scoreboard[Party.LAB],
            349,
            f"{scoreboard[Party.LAB]} should be equal to 349",
        )
        self.assertEqual(
            scoreboard[Party.CON],
            210,
            f"{scoreboard[Party.CON]} should be equal to 210",
        )
        self.assertEqual(
            scoreboard[Party.WINNER],
            "LAB",
            f"{scoreboard[Party.WINNER]} should be equal to LAB",
        )
        self.assertEqual(
            scoreboard[Party.SUM],
            650,
            f"{scoreboard[Party.SUM]} should be equal to 650",
        )


if __name__ == "__main__":
    unittest.main()
