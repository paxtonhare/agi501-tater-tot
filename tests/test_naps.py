import unittest

from run import run


class NapTests(unittest.TestCase):
    def test_disabled_drive_never_rises_or_enters_menu(self):
        baseline = run(1, 65, "baseline")
        awake = run(1, 65, "baseline", naps="off")
        self.assertTrue(any(row["action"] == "sleep" for row in baseline))
        self.assertTrue(all(row["tiredness"] == 0 and row["task"] != "sleep" for row in awake))
        self.assertEqual([row["human_room"] for row in baseline],
                         [row["human_room"] for row in awake])
