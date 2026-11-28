"""Pool counts across seeds, but never join bouts or latency windows across runs."""
from collections import Counter

from toys import TOYS, play_entropy

DRIVES = "hunger curiosity affection mischief tiredness litter".split()


def table(headers, records):
    return "\n".join("| " + " | ".join(map(str, row)) + " |"
                     for row in (headers, ["---"] * len(headers), *records))


def show(value):
    return "—" if value is None else value


def q1(results):
    records, work = [], []
    for case in ("baseline", "finish", "reward-attention", "damping-off", "naps-off"):
        rows = results[case]
        ticks = sum(r["steps"] for r in rows)
        bouts = {drive: [r["bouts"].get(drive, {}) for r in rows] for drive in DRIVES}
        total = {d: sum(b.get("work_ticks", 0) for b in bs) for d, bs in bouts.items()}
        counts = {d: sum(b.get("count", 0) for b in bs) for d, bs in bouts.items()}
        records.append([case, *[sum(r[k] for r in rows) for k in ("goal_flip_flops", "toy_switches")],
                        *[f"{total[d]/counts[d]:.3f}" if counts[d] else "—" for d in DRIVES]])
        work.append([case, *[f"{total[d]/ticks:.1%}" for d in DRIVES],
                     f"{(ticks - sum(total.values()))/ticks:.1%}"])
    return ("### Q1: Flip-flops and mean bout lengths in work ticks\n\n" +
            table(["Condition", "Goal", "Toy", *DRIVES], records) +
            "\n\n### Time shares (work by drive; travel separately)\n\n" +
            table(["Condition", *DRIVES, "travel"], work))


def q2(results):
    return table(["Seed", "Off: present", "Off: absent", "On: present", "On: absent"], [
        [left["seed"], *[r["knocks"][key] for r in (left, right) for key in ("present", "absent")]]
        for left, right in zip(results["baseline"], results["scolding-memory-on"], strict=True)])


def bag(results):
    records = []
    for setting in ("on", "off"):
        rows = results[f"bag-novelty-{setting}"]
        counts = Counter()
        for row in rows:
            counts.update(row["play_ticks"])
        entropy = play_entropy(counts)
        records.append([setting, *[counts[t] for t in TOYS], "—" if entropy is None else f"{entropy + 0.0:.3f}",
                        ", ".join(str(show(r["bag_latency"])) for r in rows)])
    return table(["Novelty", *TOYS, "Entropy (bits)", "Arrival latency, seeds 1–5"], records)


def candle(results):
    records = []
    for novelty in ("on", "off"):
        for memory in ("on", "off"):
            rows = [r["candle"] for r in results[f"candle-{novelty}-{memory}"]]
            pre, post, pre_ticks, post_ticks, singes = (sum(r[k] for r in rows) for k in
                ("before", "after", "pre_ticks", "post_ticks", "singes"))
            records.append([novelty, memory, f"{pre} / {pre_ticks}", f"{post} / {post_ticks}", singes,
                            ", ".join(str(show(r["first_singe"])) for r in rows),
                            ", ".join(str(r["final_health"]) for r in rows)])
    return table(["Novelty", "Recall", "Before: approaches / ticks", "After: approaches / ticks",
                  "Singes", "First singe by seed", "Final health by seed"], records)


def tables(results):
    return ("# Tater Tot experiment rerun\n\nFive seeds (1–5), 200 ticks each per condition.\n\n" +
            q1(results) + "\n\n### Q2: Physical knocks by human presence\n\n" + q2(results) +
            "\n\n### Q3: Paper bag at tick 100\n\n" + bag(results) +
            "\n\n### Candle at tick 100\n\n" + candle(results) + "\n")
