import unittest
import json
import os

from server import app, controller

class TestScoreboard(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.server = app.test_client()
        file_dir: str = os.path.dirname(os.path.realpath(__file__))
        self.RESULT_SAMPLE_PATH: str = f"{file_dir}/resources/sample-election-results"

    def load_and_post_result_file(self, num: str) -> dict:
        file_number: str = str(num).zfill(3)
        with open(f"{self.RESULT_SAMPLE_PATH}/result{file_number}.json", "r", encoding="utf-8") as file:
            result = file.read()
        response = self.server.post(
            "/result",
            json=json.loads(result),
            environ_overrides={"REMOTE_ADDR": f"10.0.0.{(int(num) % 250) + 1}"},
        )
        return json.loads(response.data.decode("utf-8"))

    def load_results(self, quantity: int) -> list[dict]:
        results = []
        for i in range(quantity):
            results.append(self.load_and_post_result_file(str(i + 1)))
        return results

    def fetch_scoreboard(self) -> tuple[int, dict]: # returns (status_code, response_body_object)
        response = self.server.get(
            "/scoreboard",
            environ_overrides={"REMOTE_ADDR": "10.0.1.1"},
        )
        return (response.status_code, json.loads(response.data.decode("utf-8")))

    def assert_scoreboard_has_expected_shape(self, scoreboard: dict) -> None:
        self.assertIn("seats", scoreboard)
        self.assertIn("votes", scoreboard)
        self.assertIn("voteShare", scoreboard)
        self.assertIn("declaredConstituencies", scoreboard)
        self.assertIn("totalVotesCast", scoreboard)
        self.assertIn("winner", scoreboard)

    def setUp(self) -> None:
        controller.reset()

    def test_first_5(self) -> None:
        self.load_results(5)
        status_code, scoreboard = self.fetch_scoreboard()

        self.assertEqual(status_code, 200, f"non-200 status code received: {status_code}")
        self.assertNotEqual(len(scoreboard), 0)
        self.assert_scoreboard_has_expected_shape(scoreboard)
        self.assertEqual(scoreboard["seats"].get("LD", 0), 1)
        self.assertEqual(scoreboard["seats"].get("LAB", 0), 4)
        self.assertIsNone(scoreboard["winner"])

    def test_first_100(self) -> None:
        self.load_results(100)
        status_code, scoreboard = self.fetch_scoreboard()

        self.assertEqual(status_code, 200, f"non-200 status code received: {status_code}")
        self.assertNotEqual(len(scoreboard), 0)
        self.assert_scoreboard_has_expected_shape(scoreboard)
        self.assertEqual(scoreboard["seats"].get("LD", 0), 12)
        self.assertEqual(scoreboard["seats"].get("LAB", 0), 56)
        self.assertEqual(scoreboard["seats"].get("CON", 0), 31)
        self.assertIsNone(scoreboard["winner"])

    def test_first_554(self) -> None:
        self.load_results(554)
        status_code, scoreboard = self.fetch_scoreboard()

        self.assertEqual(status_code, 200, f"non-200 status code received: {status_code}")
        self.assertNotEqual(len(scoreboard), 0)
        self.assert_scoreboard_has_expected_shape(scoreboard)
        self.assertEqual(scoreboard["seats"].get("LD", 0), 52)
        self.assertEqual(scoreboard["seats"].get("LAB", 0), 325)
        self.assertEqual(scoreboard["seats"].get("CON", 0), 167)
        self.assertEqual(scoreboard["winner"], "LAB")

    def test_all_results(self) -> None:
        self.load_results(650)
        status_code, scoreboard = self.fetch_scoreboard()

        self.assertEqual(status_code, 200, f"non-200 status code received: {status_code}")
        self.assertNotEqual(len(scoreboard), 0)
        self.assert_scoreboard_has_expected_shape(scoreboard)
        self.assertEqual(scoreboard["seats"].get("LD", 0), 62)
        self.assertEqual(scoreboard["seats"].get("LAB", 0), 349)
        self.assertEqual(scoreboard["seats"].get("CON", 0), 210)
        self.assertEqual(scoreboard["winner"], "LAB")
        self.assertEqual(sum(scoreboard["seats"].values()), 650)
        self.assertAlmostEqual(sum(scoreboard["voteShare"].values()), 100.0, places=1)

if __name__ == "__main__":
    unittest.main()
