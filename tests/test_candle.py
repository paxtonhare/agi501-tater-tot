import unittest

from candle import candle_counts
from run import run, run_metta, summarize


class CandleTests(unittest.TestCase):
    def test_singe_records_event_and_raises_risk_after_fear_decays(self):
        out = run_metta("""!(import! &self run)
!(println! (OUTCOME (candleOutcome inspect-candle 1 (100 0))))
!(println! (OUTCOME (candleOutcome inspect-candle 0 (100 0))))
!(recordSinge &test-candle 102 candle-singed kitchen hallway)
!(println! (OUTCOME (collapse (match &test-candle $event $event))
    (candleRisk off &test-candle 0) (candleRisk on &test-candle 0)
    (candleRisk on &test-candle 100)))
!(println! (OUTCOME (candleOutcome move 0 (80 100))))
""")
        self.assertEqual([line for line in out.splitlines() if line.startswith("(OUTCOME")], [
            "(OUTCOME (inspect-candle 100 0))", "(OUTCOME (candle-singed 80 100))",
            "(OUTCOME ((cat-event 102 singe inspect-candle false)) 0.14 0.4 0.9)",
            "(OUTCOME (move 80 90))",
        ])

    def test_integrated_heat_and_first_singe(self):
        rows = run(1, 105, "baseline", candle_tick=100, candle_memory="on")
        self.assertTrue(all(r["task"] != "inspect-candle" and r["candle_risk"] == 0 for r in rows[:99]))
        approach, singe, next_tick = rows[100:103]
        self.assertEqual((approach["action"], approach["candle_risk"]), ("inspect-candle", 0.14))
        self.assertEqual((singe["action"], singe["health"], singe["fear"]), ("candle-singed", 80, 100))
        self.assertAlmostEqual(next_tick["candle_risk"], 0.90)
        counts = candle_counts(rows, 100)
        self.assertEqual((counts["before"], counts["first_singe"], counts["post_ticks"]), (1, 102, 3))

    def test_food_interrupting_a_candle_sniff_is_not_a_flip_flop(self):
        rows = run(1, 145, "baseline", candle_tick=100)
        sniff, meal = rows[-2:]
        self.assertEqual((sniff["action"], sniff["work"]), ("inspect-candle", 1))
        self.assertEqual((meal["previous_task"], meal["previous_work"], meal["task"]),
                         ("inspect-candle", 1, "eat"))
        counts = summarize([sniff, meal])
        self.assertEqual(counts["flip_flops"], 0)
        self.assertEqual(counts["goal_flip_flops"], 0)
        self.assertEqual(counts["allowed_play_to_eat"], 0)

    def test_no_singe_keeps_all_observation_time_in_before_window(self):
        rows = [dict(step=tick, health=100, action=act) for tick, act in enumerate(
            ("move", "move", "inspect-candle", "eat"), start=1)]
        self.assertEqual(candle_counts(rows, 2), dict(before=1, after=0, first_singe=None, singes=0,
                                                     pre_ticks=3, post_ticks=0, final_health=100))
