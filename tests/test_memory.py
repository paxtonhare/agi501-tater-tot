import unittest

from run import knock_counts, run_metta


class MemoryTests(unittest.TestCase):
    def test_scolding_is_recalled_by_context_and_cleared_between_runs(self):
        out = run_metta("""!(import! &self run)
!(recordScolding &test-memory 6 knock kitchen hallway)
!(recordScolding &test-memory 7 knock-scolded kitchen kitchen)
!(println! (EVENTS (collapse (match &test-memory $e $e))
    (recallScoldingRisk on &test-memory kitchen)
    (recallScoldingRisk on &test-memory hallway)
    (recallScoldingRisk off &test-memory kitchen)))
!(clearCatEvents &test-memory)
!(println! (EVENTS (catEventCount &test-memory scolding knock)))
""")
        self.assertEqual([line for line in out.splitlines() if line.startswith("(EVENTS")],
                         ["(EVENTS ((cat-event 7 scolding knock true)) 0.18 0.06 0)", "(EVENTS 0)"])

    def test_counts_attempts_not_travel(self):
        rows = [{"action": action, "task": "knock"} for action in ("move", "knock", "knock-scolded")]
        self.assertEqual(knock_counts(rows), {"present": 1, "absent": 1})
