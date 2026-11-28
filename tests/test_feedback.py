import unittest

from bouts import bout_lengths, summarize_bouts
from run import run, run_metta


class BoutTests(unittest.TestCase):
    def test_travel_does_not_count_and_completion_ends_even_same_task(self):
        rows = [dict(task=task, goal=goal, action=action, work=work)
                for task, goal, action, work in [
                    ("zip-tie", "curiosity", "move", 0),
                    ("zip-tie", "curiosity", "zip-tie", 1),
                    ("zip-tie", "curiosity", "move", 1),
                    ("cuddle", "affection", "move", 0),
                    ("cuddle", "affection", "cuddle", 1),
                    ("cuddle", "affection", "cuddle", 0),
                    ("cuddle", "affection", "cuddle", 1),
                ]]
        lengths = bout_lengths(rows)
        self.assertEqual(lengths, {"curiosity": [1], "affection": [2, 1]})
        self.assertEqual(summarize_bouts(lengths)["affection"],
                         dict(count=2, work_ticks=3, mean_ticks=1.5))


class FeedbackTests(unittest.TestCase):
    def evaluate(self, *expressions):
        stdout = run_metta("!(import! &self run)\n" + "".join(f"!{expr}\n" for expr in expressions))
        return [line for line in stdout.splitlines() if line != "true"]

    def test_relief_rewards_work_but_attention_and_reward_decay(self):
        before = "(50 20 20 20 20 20)"
        after = "(0 20 20 20 20 20)"
        self.assertEqual(self.evaluate(
            f"(updateCatFeedback eat move {before} {before} (initialFeedback))",
            f"(updateCatFeedback eat eat {before} {before} (initialFeedback))",
            f"(updateCatFeedback eat eat {before} {after} (eat 1 none 0))",
            f"(updateCatFeedback eat eat {after} {after} (eat 1 eat 0.5))",
            f"(updateCatFeedback zip-tie move {after} {after} (eat 1 eat 0.5))",
            f"(updateCatFeedback zip-tie zip-tie {after} {after} (eat 1 eat 0.5))",
        ), ["(none 0 none 0.0)", "(eat 1 none 0.0)", "(eat 0.8 eat 0.5)",
            "(eat 0.8 eat 0.325)", "(none 0 eat 0.325)", "(zip-tie 1 eat 0.325)"])

    def test_menu_keeps_all_candidates_and_hunger_can_win(self):
        candidates = "((careCandidate eat kitchen hallway 100) (toyCandidate zip-tie kitchen hallway 50 100))"
        focus = "(zip-tie 1 zip-tie 0.5)"
        menu = f"(applyCatFeedback {candidates} {focus})"
        self.assertEqual(self.evaluate(
            f"(size-atom {menu})",
            f"(actionId (cycleFinalAction (chooseCat (catStates) (openPsiStimulus 0.5 0 0.05 0.2)"
            f" {menu} reward-attention zip-tie 1)))",
        ), ["2", "eat"])

    def test_reward_boost_and_attention_discount_reach_metamo_unchanged_in_order(self):
        candidates = "((action eat (0 0 0.4 0 0 0.4 0 0) 0.02 (0.005 0 0 0 0 0 0 0)) " \
                     "(action zip-tie (0 0 0 0.5 0.5 0 0 0) 0.01 (0 0.005 0 0 0 0 0 0)))"
        self.assertEqual(self.evaluate(f"(applyCatFeedback {candidates} (eat 1 eat 0.5))"), [
            "((action eat (0.0 0.0 0.5 0.0 0.0 0.5 0.0 0.0) 0.02 (0.005 0 0 0 0 0 0 0)) "
            "(action zip-tie (0.0 0.0 0.0 0.39 0.39 0.0 0.0 0.0) 0.01 (0 0.005 0 0 0 0 0 0)))"
        ])

    def test_new_mode_reaches_picker_without_changing_human_schedule(self):
        baseline = run(1, 30, "baseline")
        feedback = run(1, 30, "reward-attention")
        self.assertEqual([r["human_room"] for r in baseline], [r["human_room"] for r in feedback])
        self.assertNotEqual([r["task"] for r in baseline], [r["task"] for r in feedback])
