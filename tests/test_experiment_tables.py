import unittest

from experiment_tables import bag, candle, q1
from experiments import DESIGN


class ExperimentTableTests(unittest.TestCase):
    def test_design_keeps_scolding_and_candle_recall_separate(self):
        self.assertEqual(len(DESIGN), 12)
        for case, flags in DESIGN.items():
            if case.startswith("candle-"):
                _, novelty, recall = case.split("-")
                self.assertEqual(flags, ("--candle-tick", "100", "--novelty", novelty,
                                         "--candle-memory", recall))

    def test_pool_bouts_by_sample_count_and_time_by_all_ticks(self):
        rows = [dict(steps=10, goal_flip_flops=2, toy_switches=1,
                     bouts={"curiosity": dict(count=count, work_ticks=work)})
                for count, work in ((1, 3), (3, 3))]
        out = q1(dict.fromkeys(("baseline", "finish", "reward-attention", "damping-off", "naps-off"), rows))
        self.assertIn("| baseline | 4 | 2 | — | 1.500 |", out)
        self.assertIn("| baseline | 0.0% | 30.0% | 0.0% | 0.0% | 0.0% | 0.0% | 70.0% |", out)

    def test_run_without_arrival_or_singe_displays_missing_data(self):
        visit = dict(play_ticks={"zip-tie": 1}, bag_latency=None)
        self.assertIn("| off | 1 | 0 | 0 | 0 | 0.000 | — |", bag(dict.fromkeys(
            ("bag-novelty-on", "bag-novelty-off"), [visit])))
        no_singe = dict(candle=dict(before=0, after=0, pre_ticks=101, post_ticks=0,
                                   singes=0, first_singe=None, final_health=100))
        out = candle({f"candle-{n}-{m}": [no_singe] for n in ("on", "off") for m in ("on", "off")})
        self.assertIn("| on | off | 0 / 101 | 0 / 0 | 0 | — | 100 |", out)
