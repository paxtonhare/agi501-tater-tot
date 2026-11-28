import unittest

from run import run, run_metta
from toys import bag_latency, play_entropy


class BagTests(unittest.TestCase):
    def test_novelty_off_zeroes_only_gNovel(self):
        out = run_metta("""!(import! &self run)
!(noveltyMenu off ((action toy (1 2 3 4 5 6 7 8) 0.1 (0 1 2 3 4 5 6 7))))
""")
        self.assertIn("((action toy (1 2 3 4 0 6 7 8) 0.1 (0 1 2 3 4 5 6 7)))", out.splitlines())

    def test_bag_is_not_available_before_arrival(self):
        baseline = run(1, 35, "baseline")
        bag = run(1, 35, "baseline", bag_tick=10)
        self.assertEqual(baseline[:9], bag[:9])
        visits = [r for r in bag if r["action"] == "paper-bag"]
        self.assertTrue(visits)
        self.assertTrue(all(r["room"] == "living-room" for r in visits))

    def test_entropy_and_latency(self):
        self.assertEqual(play_entropy(dict(a=2, b=2, c=2, d=2)), 2)
        self.assertEqual(play_entropy(dict(a=2, b=0)), 0)
        self.assertIsNone(play_entropy(dict(a=0, b=0)))
        rows = [dict(step=100, task="eat", room="living-room"),
                dict(step=102, task="paper-bag", room="hallway"),
                dict(step=103, task="paper-bag", room="living-room")]
        self.assertEqual(bag_latency(rows, 100), 3)
        self.assertIsNone(bag_latency(rows, 0))
        self.assertIsNone(bag_latency(rows[:2], 100))
