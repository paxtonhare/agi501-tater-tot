#!/usr/bin/env python3
"""Run the MeTTa simulation, validate its output, and measure Q1 switches."""
import argparse
import csv
import json
import os
from pathlib import Path
import subprocess
import tempfile

from bouts import bout_lengths, summarize_bouts
from candle import candle_counts
from toys import TOYS, bag_latency, play_counts, play_entropy

ROOT = Path(__file__).resolve().parent
DRIVES = "hunger curiosity affection mischief tiredness litter".split()
FIELDS = ["step", "room", "human_room", *DRIVES, *(
    "action goal task previous_task previous_work work glass health fear candle_risk allowed_interruption".split())]
NUMBERS = ["step", *DRIVES, "previous_work", "work", "health", "fear"]


def summarize(rows):
    counts = dict(flip_flops=0, goal_flip_flops=0, toy_switches=0,
                  allowed_play_to_eat=0, allowed_to_litter=0, woke_early=0,
                  travel_replans=0, completed_tasks=0, sleep_sessions_completed=0, litter_trips=0)
    for row in rows:
        old, new = row["previous_task"], row["task"]
        if old != "none" and old != new:
            if not row["previous_work"]:
                counts["travel_replans"] += 1
            else:
                if old == "sleep":
                    counts["woke_early"] += 1
                if row["allowed_interruption"]:
                    if new == "use-litter":
                        counts["allowed_to_litter"] += 1
                    elif old in TOYS and new == "eat":
                        counts["allowed_play_to_eat"] += 1
                else:
                    counts["flip_flops"] += 1
                    kind = "toy_switches" if old in TOYS and new in TOYS else "goal_flip_flops"
                    counts[kind] += 1
        if row["action"] != "move" and row["work"] == 0:
            counts["completed_tasks"] += 1
            if new == "sleep":
                counts["sleep_sessions_completed"] += 1
            elif new == "use-litter":
                counts["litter_trips"] += 1
    return counts


def knock_counts(rows):
    """Count physical attempts; a travel tick toward the glass is not an attempt."""
    return dict(present=sum(row["action"] == "knock-scolded" for row in rows),
                absent=sum(row["action"] == "knock" for row in rows))


def parse_steps(stdout, steps):
    rows, done = [], []
    for line in stdout.splitlines():
        if line.startswith("(CAT "):
            fields = line.removesuffix(")").split()[1:]
            row = dict(zip(FIELDS, fields, strict=True))
            for key in NUMBERS:
                row[key] = int(row[key])
            row["candle_risk"] = float(row["candle_risk"])
            allowed = row["allowed_interruption"]
            if allowed not in ("true", "false"):
                raise ValueError(f"Invalid interruption flag: {allowed}")
            row["allowed_interruption"] = allowed == "true"
            rows.append(row)
        elif line.startswith("(CAT-DONE "):
            done.append(line)
    if done != [f"(CAT-DONE {steps})"] or [r["step"] for r in rows] != list(range(1, steps + 1)):
        raise ValueError("PeTTa did not emit exactly one row per step and a completion marker")
    return rows


def run_metta(entry_source):
    """Execute a temporary MeTTa entry point relative to the simulation."""
    deps = ROOT / ".deps"
    runner = deps / "PeTTa/run.sh"
    if not runner.is_file() or not (deps / "swi/bin/swipl").is_file():
        raise ValueError("toolchain missing; run bash setup.sh first")
    env = dict(os.environ, LC_ALL="C.UTF-8", PATH=f"{deps / 'swi/bin'}:{os.environ['PATH']}")
    # PeTTa imports relative to the entry file. Use a private temporary file
    # per process so concurrent runs never overwrite one another's arguments.
    with tempfile.NamedTemporaryFile(mode="w", dir=ROOT / "sim", suffix=".metta") as entry:
        entry.write(entry_source)
        entry.flush()
        result = subprocess.run(["sh", runner, entry.name, "--silent"], env=env,
                                text=True, capture_output=True, check=False)
    if result.returncode or result.stderr:
        raise ValueError(f"PeTTa diagnostics (exit {result.returncode}):\n{result.stderr.strip()}")
    return result.stdout


def run(seed, steps, mode, *, damping="on", naps="on", memory="off", novelty="on", bag_tick=0, candle_tick=0,
        candle_memory="off", self_preservation="off"):
    toggles = (damping, naps, memory, novelty, candle_memory, self_preservation)
    if any(flag not in {"on", "off"} for flag in toggles):
        raise ValueError("damping, naps, memory, novelty, candle memory and self-preservation must be on or off")
    if any(type(tick) is not int or tick < 0 for tick in (bag_tick, candle_tick)):
        raise ValueError("prop arrival ticks must be non-negative integers")
    options = f"({damping} {naps} {memory} {novelty} {bag_tick} {candle_tick} {candle_memory} {self_preservation})"
    stdout = run_metta(f"!(import! &self run)\n!(startCatConfigured {seed} {steps} {mode} {options})\n")
    return parse_steps(stdout, steps)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--steps", type=int, default=200)
    parser.add_argument("--mode", choices=("baseline", "finish", "reward-attention"), default="baseline")
    parser.add_argument("--damping", choices=("on", "off"), default="on")
    parser.add_argument("--naps", choices=("on", "off"), default="on")
    parser.add_argument("--memory", choices=("on", "off"), default="off")
    parser.add_argument("--novelty", choices=("on", "off"), default="on")
    parser.add_argument("--bag-tick", type=int, default=0, help="tick when the paper bag appears (0 disables it)")
    parser.add_argument("--candle-tick", type=int, default=0, help="tick when the candle appears (0 disables it)")
    parser.add_argument("--candle-memory", choices=("on", "off"), default="off")
    parser.add_argument("--self-preservation", choices=("on", "off"), default="off",
                        help="raise risk of injury-causing actions as health falls (default: off)")
    parser.add_argument("--out", type=Path, default=Path("runs"))
    args = parser.parse_args()
    if not 0 <= args.seed < 2**32 or args.steps < 1:
        parser.error("seed must be in [0, 2^32) and steps must be positive")
    try:
        rows = run(args.seed, args.steps, args.mode, damping=args.damping, naps=args.naps,
                   memory=args.memory, novelty=args.novelty, bag_tick=args.bag_tick, candle_tick=args.candle_tick,
                   candle_memory=args.candle_memory, self_preservation=args.self_preservation)
    except ValueError as exc:
        parser.exit(1, f"{exc}\n")
    toys = play_counts(rows)
    summary = dict(candle_tick=args.candle_tick, candle_memory=args.candle_memory, self_preservation=args.self_preservation,
                   candle=candle_counts(rows, args.candle_tick), novelty=args.novelty, bag_tick=args.bag_tick, play_ticks=toys,
                   play_entropy_bits=play_entropy(toys), bag_latency=bag_latency(rows, args.bag_tick), picker="MetaMo", seed=args.seed, steps=args.steps, mode=args.mode,
                   damping=args.damping, naps=args.naps, memory=args.memory, knocks=knock_counts(rows),
                   bouts=summarize_bouts(bout_lengths(rows)), **summarize(rows))
    args.out.mkdir(exist_ok=True, parents=True)
    suffix = "" if args.damping == "on" else "-damping-off"
    if args.naps == "off":
        suffix += "-naps-off"
    if args.memory == "on":
        suffix += "-memory-on"
    if args.novelty == "off":
        suffix += "-novelty-off"
    if args.bag_tick:
        suffix += f"-bag{args.bag_tick}"
    if args.candle_tick:
        suffix += f"-candle{args.candle_tick}"
    if args.candle_memory == "on":
        suffix += "-candle-memory-on"
    if args.self_preservation == "on":
        suffix += "-self-preservation-on"
    stem = args.out / f"{args.mode}{suffix}-{args.seed}-{args.steps}"
    with stem.with_suffix(".csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    text = json.dumps(summary)
    stem.with_suffix(".json").write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
