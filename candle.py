"""Candle experiment conditions and encounter counts."""

from itertools import product


def candle_conditions():
    for novelty, recall, preservation in product(("on", "off"), ("on", "off"), ("off", "on")):
        name = f"candle-{novelty}-{recall}"
        if preservation == "on":
            name += "-self-preservation-on"
        yield name, novelty, recall, preservation


def candle_counts(rows, arrival):
    first = next((row["step"] for row in rows if row["action"] == "candle-singed"), None)
    approaches = [row["step"] for row in rows if row["action"] == "inspect-candle"]
    return dict(before=sum(first is None or tick < first for tick in approaches),
                after=sum(first is not None and tick > first for tick in approaches),
                first_singe=first, singes=sum(row["action"] == "candle-singed" for row in rows),
                pre_ticks=sum(arrival > 0 and row["step"] >= arrival and
                              (first is None or row["step"] < first) for row in rows),
                post_ticks=sum(first is not None and row["step"] > first for row in rows),
                final_health=rows[-1]["health"])
