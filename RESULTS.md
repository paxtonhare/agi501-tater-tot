# Preliminary results: Tater Tot

**Tater Tot runs end to end in MeTTa.** MetaMo picks every action. With sleep and litter added, she finished three or four naps per 200 ticks. The “finish what you started” rule still prevented disallowed switches, but she could leave tasks for food or the litter box where the rules allow it.

## What ran

- **Toolchain:** [PeTTa v1.0.2, the pinned MetaMo revision, and SWI-Prolog 9.3.36](README.md#reproduce-on-debian-12-linux). The pinned MetaMo README names PeTTa but does not specify a version. The v1.0.2 pin worked without patching either upstream project.
- **Upstream trading example:** 106 step rows across four scenarios. The final portfolio values printed by this run were `vshape 137.76`, `choppy 100.96`, `downtrend 82.47`, and `realistic 112.35`. Step 1 in `vshape` was `buy` at `10.2` with portfolio value `100.0`.
- **Cat:** For each version, five seeds (1–5), 200 ticks each, in each mode. The same seed gives Paxton the same room schedule in both modes. The only toggle is whether to restrict the menu after work starts. These are paired debug runs, not estimates for a real cat or for other MetaMo adapters.

## Q1: Did she abandon tasks?

### First version (4 drives)

In the [first version](https://github.com/paxtonhare/agi501-tater-tot/pull/1), a flip-flop is a switch after at least one tick of actual work and before the task finishes. Leaving play to eat is allowed. A toy-to-toy switch interrupts a task without changing the curiosity goal, so the table separates those from true goal changes. Changing her mind while still on the way is counted separately.

| Seed | Baseline flip-flops (goal / toy) | Finish flip-flops | Allowed play → eat (baseline / finish) | Tasks completed (baseline / finish) |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 29 (14 / 15) | 0 | 8 / 23 | 43 / 46 |
| 2 | 33 (16 / 17) | 0 | 5 / 21 | 41 / 47 |
| 3 | 30 (16 / 14) | 0 | 9 / 23 | 41 / 41 |
| 4 | 30 (13 / 17) | 0 | 6 / 21 | 40 / 50 |
| 5 | 31 (15 / 16) | 0 | 8 / 25 | 40 / 42 |
| **Total** | **153 (74 / 79)** | **0** | **36 / 113** | **205 / 226** |

The baseline finished **zero play bouts** in 1,000 ticks even though it played with all three toys. Finish mode completed **12 play bouts**. Travel replans fell from **60 to 41**, but were not prohibited. The zero is expected: finish mode removes candidates that would count as a flip-flop rather than teaching MetaMo to prefer continuity. We did not run with damping disabled, so this does not tell us how many switches damping prevented.

#### A few real ticks (4 drives, seed 1, baseline)

| Tick | Room after action | Hunger | Curiosity | What happened |
| ---: | --- | ---: | ---: | --- |
| 3 | Kitchen | 46 | 43 | She heads for the bowl. |
| 5 | Kitchen | 60 | 55 | Still eating; two of three work ticks done. |
| 6 | Kitchen | 4 | 61 | She finishes eating. |
| 7 | Kitchen | 11 | 67 | She starts playing with the zip tie. |
| 8 | Hallway | 18 | 73 | She leaves it for the cardboard box: a flip-flop, even though she's still curious. |
| 79 | Kitchen | 51 | 100 | She knocks the glass down with Paxton there and gets scolded. |

In the paired finish run she stays with the zip tie at tick 8 and finishes at tick 9, dropping curiosity to 16.

### Second version (6 drives)

Leaving any started task to use the litter box is allowed, as is leaving play or sleep to eat. “Woke early” means she started sleeping and switched away before finishing, even if the switch was allowed. A change of plan before doing any work is counted separately. The paired counts below are baseline / finish; completed tasks include naps and litter trips.

| Seed | Baseline flip-flops (goal / toy) | Finish flip-flops | Allowed play → eat | Tasks completed | Allowed → litter | Woke early | Naps completed | Litter trips |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 16 (8 / 8) | 0 | 8 / 14 | 49 / 50 | 4 / 4 | 0 / 1 | 3 / 3 | 9 / 10 |
| 2 | 16 (9 / 7) | 0 | 8 / 10 | 47 / 48 | 4 / 8 | 1 / 0 | 3 / 3 | 9 / 10 |
| 3 | 14 (6 / 8) | 0 | 8 / 13 | 48 / 49 | 5 / 5 | 0 / 0 | 4 / 3 | 9 / 10 |
| 4 | 18 (11 / 7) | 0 | 5 / 17 | 47 / 46 | 4 / 3 | 1 / 0 | 3 / 3 | 8 / 10 |
| 5 | 14 (8 / 6) | 0 | 6 / 16 | 48 / 47 | 5 / 5 | 1 / 0 | 3 / 3 | 9 / 10 |
| **Total** | **78 (42 / 36)** | **0** | **35 / 70** | **239 / 240** | **22 / 25** | **3 / 1** | **16 / 15** | **44 / 50** |

Baseline flip-flops (disallowed switches after work started) fell from **153 to 78**. Toy-to-toy switches alone fell from **79 to 36**, so the new exceptions aren't the whole story. The new tasks took up some of the ticks previously available to play, and sleep itself added three flip-flops, all for cuddles. Finish mode still had zero by design; its one early wake was for food. Since both the available tasks and the rules changed, these runs don't isolate the effect of sleep alone. She changed plans while traveling 32 times in baseline and 38 in finish, down from 60 and 41 in the first version.

#### A few real ticks (6 drives, seed 1, baseline)

| Tick | Room | What happened |
| ---: | --- | --- |
| 24 | Hallway | She finishes her second work tick at the litter box and the litter meter drops to zero. |
| 53 | Bedroom | She starts a nap with tiredness at 100. |
| 58 | Bedroom | She finishes the sixth tick of her nap and tiredness drops to zero. |

### Follow-up: reward + attention (6 drives)

`--mode reward-attention` never removes a candidate. Starting work captures attention for that task; it keeps 80% of its strength each tick on the same task. A different destination drops the old focus. Switching can discount an alternative's goal correlations by up to 22%. When work lowers a drive, the amount relieved (as a share of 100) becomes a reward for that task; on ticks with no relief it keeps 65% of its strength. A full-strength reward can boost that task's goal correlations by up to 50%. These correlations tell MetaMo how much an action serves each goal. MetaMo's global stimulus, risk, and default damping (which limits updates to its internal goals) are unchanged. The reward and attention settings were tested together, so this comparison doesn't separate their effects.

Five paired seeds (1–5), 200 ticks per seed and mode. Baseline and finish reproduced the earlier goal/toy counts for every seed.

| Mode | Goal flip-flops | Toy flip-flops | Total | Travel replans | Allowed play → eat | Tasks completed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 42 | 36 | 78 | 32 | 35 | 239 |
| Finish | 0 | 0 | 0 | 38 | 70 | 240 |
| Reward + attention | 42 | 16 | 58 | 38 | 37 | 236 |

| Seed | Reward + attention (goal / toy) |
| ---: | ---: |
| 1 | 6 / 3 |
| 2 | 12 / 3 |
| 3 | 9 / 2 |
| 4 | 8 / 4 |
| 5 | 7 / 4 |

Mean bout lengths below pool work ticks and bout counts across seeds. A bout starts once she does work on a task and ends when she finishes or switches. Travel does not count; the work already done in a bout open at tick 200 does.

| Mode | All bouts (count) | Play | Eat | Cuddle | Knock | Sleep | Litter |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 1.94 (375) | 1.00 | 2.98 | 1.96 | 1.00 | 5.63 | 2.00 |
| Finish | 2.17 (338) | 1.40 | 2.98 | 2.00 | 1.00 | 5.71 | 2.00 |
| Reward + attention | 2.17 (343) | 1.63 | 2.99 | 2.00 | 1.00 | 6.00 | 2.00 |

**What surprised us:** The soft preference cut toy switches from 36 to 16, but goal switches still totaled 42. Play bouts averaged more work ticks than in finish mode, which still allows food and litter interruptions. Reward arrives only after a task relieves a drive, so it can't directly reward the first tick of an unfinished play bout. The toy's falling interest can still beat the attention bonus. In a smoke trial, putting the switching cost into MetaMo's risk input instead (adding up to 0.12 risk) produced exactly the same 200 action rows as baseline for seed 1; the reported experiment discounts expected payoff instead of treating reorienting as danger.

#### A few real ticks (seed 1, reward + attention)

| Tick | What happened |
| ---: | --- |
| 7–9 | She plays with the zip tie for two ticks, then leaves for the box. In baseline she leaves after one; in finish mode she stays for all three. |
| 15–17 | She plays with the catnip mouse twice, then heads for food with hunger at 81. Attention didn't make her finish playing. |
| 18–23 | She stops at the litter box, then goes to the kitchen and finishes eating. Hunger falls from 100 to 37. |

## Problems and design choices

- Debian's SWI-Prolog 9.0.4 reported `` source_sink `library(janus)' does not exist `` and then `Unknown procedure: py_call/2`. Janus lets MeTTa call MetaMo's NumPy helpers. A first source build also failed with `No source for some required packages` when the package was called `janus` instead of `swipy`. Building 9.3.36 with `swipy` fixed it. `LC_ALL=C.UTF-8` avoids the `Illegal multibyte Sequence` warnings seen on the initial attempt.
- The trading agent uses two motivational subsystems that must agree. This slice uses one, via the same default cycle API. Cat needs feed the candidate scores; MetaMo's internal goals and mood-like weights carry over between steps. Its damping limits internal updates; it is not a lock on the previously selected task.
- Toy interest drops on every play tick, but curiosity drops only when the whole bout finishes. That makes trying a fresh toy tempting before the current bout is done. This trade-off is in our adapter and world rules, not just in MetaMo.

## What remains

- **Q1:** The soft preference comparison is above. Next, compare damping on and off with the same baseline adapter and isolate the effect of removing naps.
- **Q2:** Store each scolding as an Atomspace event with time, action and human presence. Let recalled events affect candidate risk. Compare knock rates with and without memory, split by whether Paxton is present and the glass is available. Current presence changes risk directly; it is not learned.
- **Q3:** Toggle MetaMo's novelty contribution separately from toy interest. Measure the share of play per toy, ticks to first bag interaction, and candle approach rate. No novelty toggle has been implemented or tested yet.
- **Paper bag and candle:** Both are location hooks only. Add a scheduled mid-run bag arrival. For the candle, model heat as initial risk, then a singe that lowers health and raises fear, plus a memory that makes repeat approaches less appealing.
