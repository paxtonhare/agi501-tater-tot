"""Measure how much work Tater Tot does before completing or leaving a task."""
from collections import defaultdict
from statistics import mean


def bout_lengths(rows):
    """Work ticks per started task, grouped by drive; never count travel.

    An interrupted task counts up to its last work tick. Completed tasks
    end a bout even if the next task has the same ID. Include a partial bout
    observed at the end of a run, and call this separately for each run.
    """
    lengths = defaultdict(list)
    task, goal, work = None, None, 0
    for row in rows:
        if work and row["task"] != task:
            lengths[goal].append(work)
            work = 0
        task, goal = row["task"], row["goal"]
        if row["action"] != "move":
            work += 1
            if row["work"] == 0:
                lengths[goal].append(work)
                work = 0
    if work:
        lengths[goal].append(work)
    return dict(lengths)


def summarize_bouts(lengths):
    """Emit counts and means; keep integer totals for pooling across seeds."""
    return {goal: dict(count=len(ticks), work_ticks=sum(ticks), mean_ticks=round(mean(ticks), 3))
            for goal, ticks in sorted(lengths.items())}
