import unittest, json, os
from model.model import PartyEnum
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

    def fetch_scoreboard(self) -> list[dict]:
        response = self.server.get("/scoreboard")
        return (
            []
            if response.data == b"{}\n"
            else json.loads(response.data.decode("utf-8"))
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
        scoreboard = self.fetch_scoreboard()
        self.assertNotEqual(len(scoreboard), 0)
        self.assertEqual(scoreboard["LD"], 1, f"Should be LD == 1")
        self.assertEqual(scoreboard[PartyEnum.LAB], 4, f"Should be LAB == 4")
        self.assertEqual(
            scoreboard[PartyEnum.WINNER], PartyEnum.NOONE, f"Should be winner = noone"
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

        self.assertEqual(scoreboard[PartyEnum.LD], 12, f"LD == 12")
        self.assertEqual(scoreboard[PartyEnum.LAB], 56, f"LAB == 56")
        self.assertEqual(scoreboard[PartyEnum.CON], 31, f"CON == 31")
        self.assertEqual(
            scoreboard[PartyEnum.WINNER], PartyEnum.NOONE, f"winner = noone"
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
        self.assertNotEqual(len(scoreboard), 0)
        self.assertEqual(scoreboard[PartyEnum.LD], 52, f"LD == 52")
        self.assertEqual(scoreboard[PartyEnum.LAB], 325, f"LAB == 325")
        self.assertEqual(scoreboard[PartyEnum.CON], 167, f"CON == 167")
        self.assertEqual(scoreboard[PartyEnum.WINNER], PartyEnum.LAB, f"winner == LAB")

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
        self.assertEqual(scoreboard[PartyEnum.LD], 62, f"LD == 62")
        self.assertEqual(scoreboard[PartyEnum.LAB], 349, f"LAB == 349")
        self.assertEqual(scoreboard[PartyEnum.CON], 210, f"CON == 210")
        self.assertEqual(scoreboard[PartyEnum.WINNER], PartyEnum.LAB, f"winner == LAB")
        self.assertEqual(scoreboard[PartyEnum.SUM], 650, f"sum == 650")


if __name__ == "__main__":
    unittest.main()
