import unittest

from run import parse_steps, run, summarize


class MeasurementTests(unittest.TestCase):
    def test_distinguishes_bad_switches_from_hunger_priority_and_travel(self):
        def row(old, new, prior, action="move", work=0):
            return dict(previous_task=old, task=new, previous_work=prior, action=action, work=work)

        counts = summarize([
            row("eat", "zip-tie", 1), row("zip-tie", "eat", 1),
            row("zip-tie", "catnip-mouse", 1), row("cuddle", "eat", 0),
            row("eat", "eat", 2, "eat"), row("none", "cuddle", 0, "cuddle", 1),
        ])
        self.assertEqual(counts, dict(flip_flops=2, goal_flip_flops=1, toy_switches=1,
                                      allowed_play_to_eat=1, travel_replans=1, completed_tasks=1))

    def test_incomplete_or_nondeterministic_output_is_rejected(self):
        line = "(CAT 1 kitchen hallway 9 10 11 12 move hunger eat none 0 0 table)\n"
        self.assertEqual(parse_steps(line + "(CAT-DONE 1)\n", 1)[0]["task"], "eat")
        for bad in (line, line * 2 + "(CAT-DONE 1)\n", line + "(CAT-DONE 2)\n"):
            with self.assertRaises(ValueError):
                parse_steps(bad, 1)


class PeTTaTests(unittest.TestCase):
    def test_seed_replay_and_finish_mode(self):
        baseline = run(1, 40, "baseline")
        self.assertEqual(baseline, run(1, 40, "baseline"))
        finish = run(1, 40, "finish")
        self.assertEqual([r["human_room"] for r in baseline], [r["human_room"] for r in finish])
        self.assertGreater(len({r["human_room"] for r in baseline}), 1)
        self.assertGreater(summarize(baseline)["flip_flops"], 0)
        self.assertEqual(summarize(finish)["flip_flops"], 0)
        self.assertGreater(summarize(finish)["allowed_play_to_eat"], 0)
        for row in baseline + finish:
            self.assertTrue(all(0 <= row[drive] <= 100 for drive in
                                ("hunger", "curiosity", "affection", "mischief")))
            if row["action"] == "eat":
                self.assertEqual(row["room"], "kitchen")
            elif row["action"] == "cuddle":
                self.assertEqual(row["room"], row["human_room"])
            elif row["action"].startswith("knock"):
                self.assertEqual(row["glass"], "floor")
                self.assertEqual(row["action"] == "knock-scolded", row["human_room"] == "kitchen")


if __name__ == "__main__":
    unittest.main()
