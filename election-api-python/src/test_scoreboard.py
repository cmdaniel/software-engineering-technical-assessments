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
            scoreboard[Party.LD], 1, f"Expected LD==1 but got {scoreboard[Party.LD]}"
        )
        self.assertEqual(
            scoreboard[Party.LAB], 4, f"Expected LAB==4 but got {scoreboard[Party.LAB]}"
        )
        self.assertEqual(
            scoreboard[Party.WINNER],
            "noone",
            f"Expected WINNER==noone but got {scoreboard[Party.WINNER]}",
        )

    def test_first_100(self) -> None:
        """
        # assert LD == 12
        # assert LAB == 56
        # assert CON == 31
        # assert winner = noone
        """
        self.load_results(100)
        status_code, scoreboard = self.fetch_scoreboard()

        self.assertEqual(
            status_code, 200, f"non-200 status code received: {status_code}"
        )
        self.assertNotEqual(len(scoreboard), 0)
        self.assertEqual(
            scoreboard[Party.LD], 12, f"Expected LD==12 but got {scoreboard[Party.LD]}"
        )
        self.assertEqual(
            scoreboard[Party.LAB],
            56,
            f"Expected LAB==56 but got {scoreboard[Party.LAB]}",
        )
        self.assertEqual(
            scoreboard[Party.CON],
            31,
            f"Expected CON==31 but got {scoreboard[Party.CON]}",
        )
        self.assertEqual(
            scoreboard[Party.WINNER],
            "noone",
            f"Expected WINNER==noone but got {scoreboard[Party.WINNER]}",
        )

    def test_first_554(self) -> None:
        """
        # assert LD == 52
        # assert LAB = 325
        # assert CON = 167
        # assert winner = LAB
        """
        self.load_results(554)
        status_code, scoreboard = self.fetch_scoreboard()

        self.assertEqual(
            status_code, 200, f"non-200 status code received: {status_code}"
        )
        self.assertNotEqual(len(scoreboard), 0)

        self.assertEqual(
            scoreboard[Party.LD], 52, f"Expected LD==52 but got {scoreboard[Party.LD]}"
        )
        self.assertEqual(
            scoreboard[Party.LAB],
            325,
            f"Expected LAB==325 but got {scoreboard[Party.LAB]}",
        )
        self.assertEqual(
            scoreboard[Party.CON],
            167,
            f"Expected CON==167 but got {scoreboard[Party.CON]}",
        )
        self.assertEqual(
            scoreboard[Party.WINNER],
            "LAB",
            f"Expected WINNER==LAB but got {scoreboard[Party.WINNER]}",
        )

    def test_all_results(self) -> None:
        """
        # assert LD == 62
        # assert LAB == 349
        # assert CON == 210
        # assert winner = LAB
        # assert sum = 650
        """
        self.load_results(650)
        status_code, scoreboard = self.fetch_scoreboard()

        self.assertEqual(
            status_code, 200, f"non-200 status code received: {status_code}"
        )
        self.assertNotEqual(len(scoreboard), 0)
        self.assertEqual(
            scoreboard[Party.LD], 62, f"Expected LD==62 but got {scoreboard[Party.LD]}"
        )
        self.assertEqual(
            scoreboard[Party.LAB],
            349,
            f"Expected LAB==349 but got {scoreboard[Party.LAB]}",
        )
        self.assertEqual(
            scoreboard[Party.CON],
            210,
            f"Expected CON==210 but got {scoreboard[Party.CON]}",
        )
        self.assertEqual(
            scoreboard[Party.WINNER],
            "LAB",
            f"Expected WINNER==LAB but got {scoreboard[Party.WINNER]}",
        )
        self.assertEqual(
            scoreboard[Party.SUM],
            650,
            f"Expected SUM==650 but got {scoreboard[Party.SUM]}",
        )


if __name__ == "__main__":
    unittest.main()
