import unittest

from run import DRIVES, parse_steps, run, summarize


def row(old, new, prior, action="move", work=0, *, allowed=False):
    return dict(previous_task=old, task=new, previous_work=prior, action=action, work=work,
                allowed_interruption=allowed)


class MeasurementTests(unittest.TestCase):
    def test_distinguishes_bad_switches_from_hunger_priority_and_travel(self):
        counts = summarize([
            row("eat", "zip-tie", 1), row("zip-tie", "eat", 1, allowed=True),
            row("zip-tie", "catnip-mouse", 1), row("cuddle", "eat", 0),
            row("eat", "eat", 2, "eat"), row("none", "cuddle", 0, "cuddle", 1),
        ])
        self.assertEqual(counts, dict(flip_flops=2, goal_flip_flops=1, toy_switches=1,
                                      allowed_play_to_eat=1, allowed_to_litter=0, woke_early=0,
                                      travel_replans=1, completed_tasks=1, sleep_sessions_completed=0,
                                      litter_trips=0))

    def test_litter_can_interrupt_any_other_started_task(self):
        for old in ("eat", "zip-tie", "cardboard-box", "catnip-mouse", "cuddle", "knock", "sleep"):
            with self.subTest(old=old):
                counts = summarize([row(old, "use-litter", 1, allowed=True)])
                self.assertEqual(counts["allowed_to_litter"], 1)
                self.assertEqual(counts["woke_early"], int(old == "sleep"))
                self.assertEqual(counts["flip_flops"], 0)

    def test_sleep_interruptions(self):
        for new in ("eat", "use-litter", "zip-tie", "cuddle", "knock"):
            with self.subTest(new=new):
                allowed = new in {"eat", "use-litter"}
                counts = summarize([row("sleep", new, 2, allowed=allowed)])
                forbidden = int(not allowed)
                self.assertEqual(counts["flip_flops"], forbidden)
                self.assertEqual(counts["goal_flip_flops"], forbidden)
                self.assertEqual(counts["allowed_play_to_eat"], 0)
                self.assertEqual(counts["woke_early"], 1)

    def test_travel_to_sleep_or_litter_is_not_work(self):
        counts = summarize([row("sleep", "use-litter", 0), row("use-litter", "eat", 0)])
        self.assertEqual(counts["travel_replans"], 2)
        for key in ("allowed_to_litter", "woke_early", "sleep_sessions_completed", "litter_trips"):
            self.assertEqual(counts[key], 0)

    def test_only_completed_naps_and_litter_trips_are_counted(self):
        counts = summarize([
            row("none", "sleep", 0), row("sleep", "sleep", 0, "sleep", 1),
            row("sleep", "sleep", 5, "sleep"), row("none", "use-litter", 0),
            row("use-litter", "use-litter", 0, "use-litter", 1),
            row("use-litter", "use-litter", 1, "use-litter"),
            row("use-litter", "knock", 1, "knock"),
        ])
        self.assertEqual(counts["sleep_sessions_completed"], 1)
        self.assertEqual(counts["litter_trips"], 1)
        self.assertEqual(counts["completed_tasks"], 3)
        self.assertEqual(counts["flip_flops"], 1)
        self.assertEqual(counts["woke_early"], 0)

    def test_incomplete_or_nondeterministic_output_is_rejected(self):
        line = "(CAT 1 kitchen hallway 9 10 11 12 13 14 move hunger eat none 0 0 table 100 0 0 false)\n"
        parsed = parse_steps(line + "(CAT-DONE 1)\n", 1)[0]
        self.assertEqual((parsed["task"], parsed["tiredness"], parsed["litter"]), ("eat", 13, 14))
        self.assertIs(parsed["allowed_interruption"], False)
        for bad in (line, line * 2 + "(CAT-DONE 1)\n", line + "(CAT-DONE 2)\n"):
            with self.assertRaises(ValueError):
                parse_steps(bad, 1)


class PeTTaTests(unittest.TestCase):
    def test_seed_replay_and_finish_mode(self):
        baseline = run(1, 75, "baseline")
        self.assertEqual(baseline, run(1, 75, "baseline"))
        finish = run(1, 75, "finish")
        self.assertEqual([r["human_room"] for r in baseline], [r["human_room"] for r in finish])
        self.assertGreater(len({r["human_room"] for r in baseline}), 1)
        self.assertGreater(summarize(baseline)["flip_flops"], 0)
        self.assertEqual(summarize(finish)["flip_flops"], 0)
        self.assertGreater(summarize(finish)["allowed_play_to_eat"], 0)
        self.assertGreater(summarize(finish)["allowed_to_litter"], 0)
        for trial in (baseline, finish):
            self.check_bodily_needs(trial)
        for row in baseline + finish:
            self.assertTrue(all(0 <= row[drive] <= 100 for drive in DRIVES))
            if row["action"] == "eat":
                self.assertEqual(row["room"], "kitchen")
            elif row["action"] == "cuddle":
                self.assertEqual(row["room"], row["human_room"])
            elif row["action"].startswith("knock"):
                self.assertEqual(row["glass"], "floor")
                self.assertEqual(row["action"] == "knock-scolded", row["human_room"] == "kitchen")

    def check_bodily_needs(self, rows):
        tiredness, litter, boost = 0, 0, 0
        naps, litter_trips = 0, 0
        for tick in rows:
            action, work = tick["action"], tick["work"]
            prior = tick["previous_work"] if tick["previous_task"] == action else 0
            if action == "sleep":
                self.assertEqual(tick["room"], "bedroom")
                self.assertEqual(work, (prior + 1) % 6)
            if action == "use-litter":
                self.assertEqual(tick["room"], "hallway")
                self.assertEqual(work, (prior + 1) % 2)
            slept = action == "sleep" and work == 0
            used_litter = action == "use-litter" and work == 0
            naps += slept
            litter_trips += used_litter
            tiredness = 0 if slept else min(100, tiredness + 2)
            litter = 0 if used_litter else min(100, litter + (8 if boost else 3))
            self.assertEqual((tick["tiredness"], tick["litter"]), (tiredness, litter))
            boost = 5 if action == "eat" and work == 0 else max(0, boost - 1)
        self.assertGreater(naps, 0)
        self.assertGreater(litter_trips, 0)


if __name__ == "__main__":
    unittest.main()
