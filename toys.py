"""Measure play and directed arrival at a new toy."""
from collections import Counter
from math import log2

TOYS = ("zip-tie", "cardboard-box", "catnip-mouse", "paper-bag")


def play_counts(rows):
    counts = Counter(row["action"] for row in rows)
    return {toy: counts[toy] for toy in TOYS}


def play_entropy(counts):
    total = sum(counts.values())
    if not total:
        return None
    shares = [count / total for count in counts.values() if count]
    return round(-sum(share * log2(share) for share in shares), 3)


def bag_latency(rows, arrival):
    if not arrival:
        return None
    return next((row["step"] - arrival for row in rows if row["step"] >= arrival
                 and row["task"] == "paper-bag" and row["room"] == "living-room"), None)
