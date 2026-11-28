#!/usr/bin/env python3
"""Rerun the final-report matrix on seeds 1–5, 200 ticks each."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys

from experiment_tables import tables

ROOT = Path(__file__).resolve().parent
SEEDS = range(1, 6)
DESIGN = {
    "baseline": (),
    "finish": ("--mode", "finish"),
    "reward-attention": ("--mode", "reward-attention"),
    "damping-off": ("--damping", "off"),
    "naps-off": ("--naps", "off"),
    "scolding-memory-on": ("--memory", "on"),
    "bag-novelty-on": ("--bag-tick", "100"),
    "bag-novelty-off": ("--bag-tick", "100", "--novelty", "off"),
    **{f"candle-{novelty}-{memory}": ("--candle-tick", "100", "--novelty", novelty,
                                    "--candle-memory", memory)
       for novelty in ("on", "off") for memory in ("on", "off")},
}


def trial(out, case, seed):
    command = [sys.executable, str(ROOT / "run.py"), "--out", str(out / case),
               "--seed", str(seed), "--steps", "200", *DESIGN[case]]
    proc = subprocess.run(command, capture_output=True, text=True)
    if proc.returncode:
        raise RuntimeError(f"{case}, seed {seed}: {proc.stderr.strip()}")
    return case, json.loads(proc.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "runs" / "experiments")
    parser.add_argument("--jobs", type=int, default=1, help="parallel PeTTa processes")
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be positive")
    args.out.mkdir(parents=True, exist_ok=True)
    summary = args.out / "summary.md"
    # Never leave a previous summary in place if this rerun fails.
    summary.unlink(missing_ok=True)
    if not (ROOT / ".deps/swi/bin/swipl").is_file() or not (ROOT / ".deps/PeTTa/run.sh").is_file():
        subprocess.run(["bash", str(ROOT / "setup.sh")], cwd=ROOT, check=True)
    results = {case: [] for case in DESIGN}
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        trials = (pool.submit(trial, args.out, case, seed) for case in DESIGN for seed in SEEDS)
        for future in list(trials):
            case, row = future.result()
            results[case].append(row)
    summary.write_text(tables(results), encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
