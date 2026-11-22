# Preliminary results: Tater Tot

**Tater Tot runs end to end in MeTTa.** MetaMo picks every action. Its default damping (limiting changes to its internal motivation) did not stop Tater Tot from abandoning tasks in this house. A first “finish what you started” rule stopped the counted switches, but she still dropped play for food often.

## What ran

- **Toolchain:** [PeTTa v1.0.2, the pinned MetaMo revision, and SWI-Prolog 9.3.36](README.md#reproduce-on-debian-12-linux). The pinned MetaMo README names PeTTa but does not specify a version. The v1.0.2 pin worked without patching either upstream project.
- **Upstream trading example:** 106 step rows across four scenarios. The final portfolio values printed by this run were `vshape 137.76`, `choppy 100.96`, `downtrend 82.47`, and `realistic 112.35`. Step 1 in `vshape` was `buy` at `10.2` with portfolio value `100.0`.
- **Cat:** Five seeds (1–5), 200 ticks each, in each mode. The same seed gives Paxton the same room schedule in both modes. The only toggle is whether to restrict the menu after work starts. These are paired debug runs, not estimates for a real cat or for other MetaMo adapters.

## Q1: Did she abandon tasks?

A flip-flop is a switch after at least one tick of actual work and before the task finishes. Leaving play to eat is allowed. A toy-to-toy switch interrupts a task without changing the curiosity goal, so the table separates those from true goal changes. Changing her mind while still on the way is counted separately.

| Seed | Baseline flip-flops (goal / toy) | Finish flip-flops | Allowed play → eat (baseline / finish) | Tasks completed (baseline / finish) |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 29 (14 / 15) | 0 | 8 / 23 | 43 / 46 |
| 2 | 33 (16 / 17) | 0 | 5 / 21 | 41 / 47 |
| 3 | 30 (16 / 14) | 0 | 9 / 23 | 41 / 41 |
| 4 | 30 (13 / 17) | 0 | 6 / 21 | 40 / 50 |
| 5 | 31 (15 / 16) | 0 | 8 / 25 | 40 / 42 |
| **Total** | **153 (74 / 79)** | **0** | **36 / 113** | **205 / 226** |

The baseline finished **zero play bouts** in 1,000 ticks even though it played with all three toys. Finish mode completed **12 play bouts**. Travel replans fell from **60 to 41**, but were not prohibited. The zero is expected: finish mode removes candidates that would count as a flip-flop rather than teaching MetaMo to prefer continuity. We did not run with damping disabled, so this does not tell us how many switches damping prevented.

### A few real ticks (seed 1, baseline)

| Tick | Room after action | Hunger | Curiosity | What happened |
| ---: | --- | ---: | ---: | --- |
| 3 | Kitchen | 46 | 43 | She heads for the bowl. |
| 5 | Kitchen | 60 | 55 | Still eating; two of three work ticks done. |
| 6 | Kitchen | 4 | 61 | She finishes eating. |
| 7 | Kitchen | 11 | 67 | She starts playing with the zip tie. |
| 8 | Hallway | 18 | 73 | She leaves it for the cardboard box: a flip-flop, even though she's still curious. |
| 79 | Kitchen | 51 | 100 | She knocks the glass down with Paxton there and gets scolded. |

In the paired finish run she stays with the zip tie at tick 8 and finishes at tick 9, dropping curiosity to 16.

## Problems and design choices

- Debian's SWI-Prolog 9.0.4 reported `` source_sink `library(janus)' does not exist `` and then `Unknown procedure: py_call/2`. Janus lets MeTTa call MetaMo's NumPy helpers. A first source build also failed with `No source for some required packages` when the package was called `janus` instead of `swipy`. Building 9.3.36 with `swipy` fixed it. `LC_ALL=C.UTF-8` avoids the `Illegal multibyte Sequence` warnings seen on the initial attempt.
- The trading agent uses two motivational subsystems that must agree. This slice uses one, via the same default cycle API. Cat needs feed the candidate scores; MetaMo's internal goals and mood-like weights carry over between steps. Its damping limits internal updates; it is not a lock on the previously selected task.
- Toy interest drops on every play tick, but curiosity drops only when the whole bout finishes. That makes trying a fresh toy tempting before the current bout is done. This trade-off is in our adapter and world rules, not just in MetaMo.

## What remains

- **Q1:** Compare the hard menu rule with a softer preference for the current task. Try permitting play-to-eat only above a hunger threshold; report travel churn, unfinished bouts, and hunger alongside flip-flops. If testing damping itself, compare it on and off with the same adapter.
- **Q2:** Store each scolding as an Atomspace event with time, action and human presence. Let recalled events affect candidate risk. Compare knock rates with and without memory, split by whether Paxton is present and the glass is available. Current presence changes risk directly; it is not learned.
- **Q3:** Toggle MetaMo's novelty contribution separately from toy interest. Measure the share of play per toy, ticks to first bag interaction, and candle approach rate. No novelty toggle has been implemented or tested yet.
- **Paper bag and candle:** Both are location hooks only. Add a scheduled mid-run bag arrival. For the candle, model heat as initial risk, then a singe that lowers health and raises fear, plus a memory that makes repeat approaches less appealing.
