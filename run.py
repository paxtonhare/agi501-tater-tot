#!/usr/bin/env python3
"""Run the MeTTa simulation, validate its output, and measure Q1 switches."""
import argparse
import csv
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
FIELDS = ("step room human_room hunger curiosity affection mischief action "
          "goal task previous_task previous_work work glass").split()
NUMBERS = "step hunger curiosity affection mischief previous_work work".split()
TOYS = {"zip-tie", "cardboard-box", "catnip-mouse"}


def summarize(rows):
    counts = dict(flip_flops=0, goal_flip_flops=0, toy_switches=0,
                  allowed_play_to_eat=0, travel_replans=0, completed_tasks=0)
    for row in rows:
        old, new = row["previous_task"], row["task"]
        if old != "none" and old != new:
            if not row["previous_work"]:
                counts["travel_replans"] += 1
            elif old in TOYS and new == "eat":
                counts["allowed_play_to_eat"] += 1
            else:
                counts["flip_flops"] += 1
                kind = "toy_switches" if old in TOYS and new in TOYS else "goal_flip_flops"
                counts[kind] += 1
        if row["action"] != "move" and row["work"] == 0:
            counts["completed_tasks"] += 1
    return counts


def parse_steps(stdout, steps):
    rows, done = [], []
    for line in stdout.splitlines():
        if line.startswith("(CAT "):
            fields = line.removesuffix(")").split()[1:]
            row = dict(zip(FIELDS, fields, strict=True))
            for key in NUMBERS:
                row[key] = int(row[key])
            rows.append(row)
        elif line.startswith("(CAT-DONE "):
            done.append(line)
    if done != [f"(CAT-DONE {steps})"] or [r["step"] for r in rows] != list(range(1, steps + 1)):
        raise ValueError("PeTTa did not emit exactly one row per step and a completion marker")
    return rows


def run(seed, steps, mode):
    deps = ROOT / ".deps"
    runner = deps / "PeTTa/run.sh"
    if not runner.is_file() or not (deps / "swi/bin/swipl").is_file():
        raise ValueError("toolchain missing; run bash setup.sh first")
    env = dict(os.environ, LC_ALL="C.UTF-8", PATH=f"{deps / 'swi/bin'}:{os.environ['PATH']}")
    # PeTTa imports relative to the entry file. Use a private temporary file
    # per process so concurrent runs never overwrite one another's arguments.
    with tempfile.NamedTemporaryFile(mode="w", dir=ROOT / "sim", suffix=".metta") as entry:
        entry.write(f"!(import! &self run)\n!(startCat {seed} {steps} {mode})\n")
        entry.flush()
        result = subprocess.run(["sh", runner, entry.name, "--silent"], env=env,
                                text=True, capture_output=True, check=False)
    if result.returncode or result.stderr:
        raise ValueError(f"PeTTa diagnostics (exit {result.returncode}):\n{result.stderr.strip()}")
    return parse_steps(result.stdout, steps)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--steps", type=int, default=200)
    parser.add_argument("--mode", choices=("baseline", "finish"), default="baseline")
    parser.add_argument("--out", type=Path, default=Path("runs"))
    args = parser.parse_args()
    if not 0 <= args.seed < 2**32 or args.steps < 1:
        parser.error("seed must be in [0, 2^32) and steps must be positive")
    try:
        rows = run(args.seed, args.steps, args.mode)
    except ValueError as exc:
        parser.exit(1, f"{exc}\n")
    summary = dict(picker="MetaMo", seed=args.seed, steps=args.steps, mode=args.mode, **summarize(rows))
    args.out.mkdir(exist_ok=True, parents=True)
    stem = args.out / f"{args.mode}-{args.seed}-{args.steps}"
    with stem.with_suffix(".csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    text = json.dumps(summary)
    stem.with_suffix(".json").write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
