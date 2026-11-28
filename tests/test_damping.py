import unittest

from run import run, run_metta


class DampingTests(unittest.TestCase):
    def test_only_damping_hook_changes_and_differs_near_boundary(self):
        stdout = run_metta("""!(import! &self run)
!(let (metaMoPseudoBimonad $a $b $d $c $p $v $s) (catBimonad on)
    (println! (DAMPING (== (catBimonad off) (metaMoPseudoBimonad $a $b undampedDelta $c $p $v $s)))))
!(let* (($state (motivation (0.95 1 1 1 1 1 1 1) (0.5 0.5 0.5 0.5 0.5 0.5)))
        ($delta (0.1 0 0 0 0 0 0 0)))
    (println! (DAMPING (and (== (undampedDelta $state $delta) $delta)
         (< (index-atom (applyHomeostaticDamping $state $delta) 0) 0.1)))))
""")
        self.assertEqual([x for x in stdout.splitlines() if x.startswith("(DAMPING")],
                         ["(DAMPING true)"] * 2)

    def test_off_runs_with_the_same_human_schedule(self):
        on = run(1, 30, "baseline")
        off = run(1, 30, "baseline", damping="off")
        self.assertEqual([r["human_room"] for r in on], [r["human_room"] for r in off])
