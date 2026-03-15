import unittest
import json
import os
from model.model import Party
from server import app, controller
from werkzeug.test import TestResponse


class TestScoreboard(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.server = app.test_client(use_cookies=True)
        file_dir: str = os.path.dirname(os.path.realpath(__file__))
        self.RESULT_SAMPLE_PATH: str = f"{file_dir}/resources/sample-election-results"

    def load_and_post_result_file(self, num: int) -> TestResponse:
        file_number: str = str(num).zfill(3)
        with open(f"{self.RESULT_SAMPLE_PATH}/result{file_number}.json", "r") as file:
            result = file.read()
        return self.server.post("/result", json=json.loads(result))

    def load_results(self, quantity: int) -> list[dict]:
        results = []
        for i in range(quantity):
            results.append(self.load_and_post_result_file(i + 1))
        return results

    def fetch_scoreboard(self) -> tuple[int, dict]:
        response = self.server.get("/scoreboard")
        return (
            response.status_code,
            (
                {}
                if response.data == b"{}\n"
                else json.loads(response.data.decode("utf-8"))
            ),
        )

    def setUp(self) -> None:
        controller.reset()

    def test_first_5(self) -> None:
        """
        # assert LD == 1
        # assert LAB == 4
        # assert winner == noone
        """
        self.load_results(5)
        status_code, scoreboard = self.fetch_scoreboard()
        self.assertNotEqual(len(scoreboard), 0)
        self.assertEqual(
            status_code, 200, f"Status Code should be 200, but get {status_code}"
        )
        self.assertEqual(
            scoreboard[Party.LD],
            1,
            f"Should be LD == 1 but got {scoreboard[Party.LD]}",
        )
        self.assertEqual(
            scoreboard[Party.LAB],
            4,
            f"Should be LAB == 4 but got {scoreboard[Party.LAB]}",
        )
        self.assertEqual(
            scoreboard[Party.WINNER],
            Party.NOONE,
            f"Should be winner = noone but got {scoreboard[Party.WINNER]}",
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
        self.assertNotEqual(len(scoreboard), 0)
        self.assertEqual(
            status_code, 200, f"Status Code should be 200, but get {status_code}"
        )
        self.assertEqual(
            scoreboard[Party.LD],
            12,
            f" Should be LD == 12 but got {scoreboard[Party.LD]}",
        )
        self.assertEqual(
            scoreboard[Party.LAB],
            56,
            f" Should be LAB == 56 but got {scoreboard[Party.LAB]}",
        )
        self.assertEqual(
            scoreboard[Party.CON],
            31,
            f" Should be CON == 31 but got {scoreboard[Party.CON]}",
        )
        self.assertEqual(
            scoreboard[Party.WINNER],
            Party.NOONE,
            f" Should be winner = noone but got {scoreboard[Party.WINNER]}",
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
            status_code, 200, f"Status Code should be 200, but get {status_code}"
        )
        self.assertNotEqual(len(scoreboard), 0)
        self.assertEqual(
            scoreboard[Party.LD],
            52,
            f"Should be LD == 52 but got {scoreboard[Party.LD]} ",
        )
        self.assertEqual(
            scoreboard[Party.LAB],
            325,
            f"Should be LAB == 325 but got {scoreboard[Party.LAB]} ",
        )
        self.assertEqual(
            scoreboard[Party.CON],
            167,
            f"Should be CON == 167 but got {scoreboard[Party.CON]} ",
        )
        self.assertEqual(
            scoreboard[Party.WINNER],
            Party.LAB,
            f"Should be winner == LAB but got {scoreboard[Party.WINNER]} ",
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
        self.assertNotEqual(len(scoreboard), 0)
        self.assertEqual(
            status_code, 200, f"Status Code should be 200, but get {status_code}"
        )
        self.assertEqual(
            scoreboard[Party.LD],
            62,
            f"Should by LD == 62 but got {scoreboard[Party.LD]}",
        )
        self.assertEqual(
            scoreboard[Party.LAB],
            349,
            f"Should by LAB == 349 but got {scoreboard[Party.LAB]}",
        )
        self.assertEqual(
            scoreboard[Party.CON],
            210,
            f"Should by CON == 210 but got {scoreboard[Party.CON]}",
        )
        self.assertEqual(
            scoreboard[Party.WINNER],
            Party.LAB,
            f"Should by winner == LAB but got {scoreboard[Party.WINNER]}",
        )
        self.assertEqual(
            scoreboard[Party.SUM],
            650,
            f"Should by sum == 650 but got {scoreboard[Party.SUM]}",
        )


if __name__ == "__main__":
    unittest.main()
