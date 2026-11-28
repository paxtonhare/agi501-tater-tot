import unittest

from run import run, run_metta


class SelfPreservationTests(unittest.TestCase):
    def test_missing_health_raises_hazard_risk_but_only_when_enabled(self):
        out = run_metta("""!(import! &self run)
!(println! (RISKS (injuryAdjustedRisk on 100 0.14) (injuryAdjustedRisk on 80 0.14)
                  (injuryAdjustedRisk on 40 0.14) (injuryAdjustedRisk on 0 0.14)
                  (injuryAdjustedRisk off 40 0.14) (injuryAdjustedRisk off 0 0.90)))
""")
        risk_line, = [line for line in out.splitlines() if line.startswith("(RISKS ")]
        actual = map(float, risk_line.removesuffix(")").split()[1:])
        for observed, expected in zip(actual, (0.14, 0.34, 0.74, 1.0, 0.14, 0.90), strict=True):
            self.assertAlmostEqual(observed, expected)

    def test_next_decision_uses_health_only_after_the_first_singe(self):
        default = run(1, 115, "baseline", candle_tick=100)
        off = run(1, 115, "baseline", candle_tick=100, self_preservation="off")
        on = run(1, 115, "baseline", candle_tick=100, self_preservation="on")
        self.assertEqual(off, default)
        self.assertEqual(on[:102], off[:102])
        self.assertEqual((on[101]["action"], on[101]["health"]), ("candle-singed", 80))
        self.assertAlmostEqual(off[102]["candle_risk"], 0.64)
        self.assertAlmostEqual(on[102]["candle_risk"], 0.84)
        self.assertEqual((off[112]["fear"], off[112]["candle_risk"]), (0, 0.14))
        self.assertEqual(on[112]["fear"], 0)
        self.assertAlmostEqual(on[112]["candle_risk"], 0.34)
