# AGI 501 final results: Tater Tot

**MetaMo picks every action.** The finish rule eliminated disallowed switches by design. Damping barely changed this cat's behavior; removing naps increased switching. Scolding recall reduced knocks modestly, while singe recall roughly halved repeat candle approaches with novelty on. The earlier four-drive run is historical; the [rerun script](experiments.py) reproduces the current six-drive matrix and writes the summary tables.

## What ran

- **Toolchain:** [PeTTa v1.0.2, the pinned MetaMo revision, and SWI-Prolog 9.3.36](README.md#reproduce-on-debian-12-linux). The pinned MetaMo README names PeTTa but does not specify a version. The v1.0.2 pin worked without patching either upstream project.
- **Upstream trading example:** 106 step rows across four scenarios. The final portfolio values printed by this run were `vshape 137.76`, `choppy 100.96`, `downtrend 82.47`, and `realistic 112.35`. Step 1 in `vshape` was `buy` at `10.2` with portfolio value `100.0`.
- **Cat:** For each version, five seeds (1–5), 200 ticks each, in each mode. The same seed gives Paxton the same room schedule across conditions. Each comparison changes only the setting described below unless explicitly labeled as a version change. These are paired debug runs, not estimates for a real cat or for other MetaMo adapters.

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

### Damping on vs off

MetaMo's [homeostatic damping](https://github.com/iCog-Labs-Dev/MetaMo/blob/bf97e50a68aa5059457092dfbe70699b7dd1dbe2/dynamics/stability.metta) shrinks updates to its internal goal weights near a safety boundary. The switch replaces just that hook with one that returns the update unchanged. It leaves caution, projection (moving weights back inside limits), checks, fallback and blending in place. It does not change the current tick's menu.

| Damping | Goal / toy switches | Eat | Play | Cuddle | Knock | Sleep | Litter |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| On | 42 / 36 | 2.975 | 1.000 | 1.955 | 1.000 | 5.632 | 2.000 |
| Off | 42 / 36 | 2.975 | 1.000 | 1.955 | 1.000 | 5.632 | 2.000 |

Bout means pool actual work ticks per bout, not walks. **Surprise:** only one world log row changed. At seed 5, tick 200, damping on sent her toward Paxton, while damping off made her play with the zip tie. That was one extra one-tick bout, not a flip-flop. This result is about the goal-update hook in this adapter, not about removing all stabilization.

### Naps off

We held tiredness at zero before appraisal (MetaMo's read of the situation) and removed the sleep candidate. The other drives kept their usual rules. Shares use all 1,000 ticks, with travel separate rather than crediting it to the pursued drive.

| Naps | Goal / toy switches | Hunger | Curiosity | Affection | Mischief | Tiredness | Litter | Travel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| On | 42 / 36 | 23.8% | 12.9% | 13.1% | 3.6% | 10.7% | 8.8% | 27.1% |
| Off | 55 / 50 | 25.5% | 15.9% | 14.5% | 4.2% | 0.0% | 8.7% | 31.2% |

**Log, seed 1:** At tick 53, in the baseline she started a nap with tiredness at 100. Without naps she ate instead. **Surprise:** the largest increase was travel (+4.1 points), not play (+3.0). Litter work barely changed.

## Q2: Did she remember being scolded?

Each scolding becomes an Atomspace fact, for example `(cat-event 20 scolding knock true)` for seed 1 at tick 20: she knocked the glass and Paxton was in the kitchen. Recall adds 0.18 to the knock candidate's risk per scolding if Paxton is there now, or 0.06 if he isn't, up to four events. Both settings record events; only memory on reads them for scoring. A knock attempt is an actual knock, not a walk toward the glass.

| Seed | Recall off: present / absent | Recall on: present / absent |
| --- | ---: | ---: |
| 1 | 2 / 6 | 2 / 6 |
| 2 | 2 / 5 | 1 / 4 |
| 3 | 2 / 5 | 1 / 5 |
| 4 | 0 / 7 | 0 / 7 |
| 5 | 0 / 7 | 0 / 7 |
| **Total** | **6 / 30** | **4 / 29** |

**Surprise:** recall did not deter every repeat, and seeds 4 and 5 never got scolded, so there was nothing to recall. These are counts, not probabilities given an available glass: earlier knocks can change later opportunities.

## Q3: Did novelty help her discover the paper bag?

The bag appeared in the living room at tick 100 in both conditions. Novelty off zeroed each candidate's `gNovel` correlation (how strongly the action serves the novelty goal), including its contribution to the scorer's exploration bonus. It kept the separate curiosity drive, toy boredom and environmental novelty observation intact. The denominator for each toy count is the full run; latency starts at tick 100 and ends when she is in the living room pursuing the bag, not when she first walks in that direction.

| Novelty | Zip tie | Box | Mouse | Bag | Entropy (bits) | Ticks to bag, seeds 1–5 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| On | 69 | 30 | 25 | 14 | 1.760 | 48, 24, 22, 24, 33 |
| Off | 12 | 2 | 0 | 0 | 0.592 | No arrivals by tick 200 |

Entropy tells how evenly she spread play: 0 means one toy got all play, and 2 means four toys got equal play. **Log, seed 1:** At tick 148 she stopped playing with the box and played with the bag in the same room. **Surprise:** the effect wasn't just a different toy mix; play itself fell from 138 ticks to 14. This tests the novelty input for all toys, not a bonus unique to the bag.

## Candle: Did a singe deter another approach?

The candle appeared in the kitchen at tick 100, with no bag and no scolding recall. Heat starts its candidate risk at 0.14. The first in-room work tick is an approach (a sniff); the second gets too close. That records a singe, subtracts 20 health down to zero, and raises fear to 100. Fear adds risk in both memory settings and drops by 10 each non-singe tick. Recall on adds 0.26 risk per remembered singe up to three events; total candle risk is capped at 1. Neither risk source forces a choice.

| Novelty | Singe recall | Approaches / ticks before first singe | Approaches / ticks after | Total singes | Final health, seeds 1–5 |
| --- | --- | ---: | ---: | ---: | --- |
| On | On | 6 / 43 | 14 / 457 | 17 | 20, 40, 20, 40, 40 |
| On | Off | 6 / 43 | 30 / 457 | 34 | 0, 0, 0, 0, 0 |
| Off | On | 6 / 441 | 0 / 63 | 1 | 100, 100, 100, 80, 100 |
| Off | Off | 6 / 441 | 0 / 63 | 1 | 100, 100, 100, 80, 100 |

Eating after an unfinished candle sniff no longer counts as a flip-flop, matching the simulator's interruption rule.

We exclude the first singe tick from both windows. If no singe happens, all ticks since the candle appeared stay in the before window. Counts before/after aren't directly comparable without the time windows: when novelty was off, only seed 4 was singed (tick 137), so four seeds never entered the after window.

**Log, seed 1, novelty and recall on:** Tick 101: she sniffs (risk 0.14). Tick 102: she singes herself (health 80, fear 100). Tick 103: the candle's risk is 0.90 and she heads toward bed. **Surprise:** even with recall, she sometimes returned. With novelty on and recall off, all five seeds reached zero health. The sim runs to the end at zero health, so it measures injury, not death.

## Where MeTTa/Hyperon fit well vs caused friction

- **Facts and memory fit well.** Rooms, objects, scoldings and singes use the same fact-and-pattern style. `match` retrieves the event ticks without teaching the scorer about event storage. This repo tested PeTTa, not Hyperon's reference runtime. The pinned PeTTa did not support the upstream example's `(new-space)` call; it treated it as an unevaluated list. A named space with explicit clearing at run start worked.
- **Install.** Debian's SWI-Prolog 9.0.4 could not load `library(janus)` or find `py_call/2`. Janus is the bridge to MetaMo's NumPy helpers. Building pinned SWI-Prolog 9.3.36 with `swipy` (not `janus` as the package name) worked. `LC_ALL=C.UTF-8` handles the multibyte characters in the upstream source.
- **Debugging.** Import order mattered: loading the adapter before its new damping helper made a decision expression return no result. PeTTa could exit successfully without a full trace, so Python checks for each expected tick and the final marker rather than trusting the exit code alone.
- **Performance.** Even one cat inherits MetaMo's appraisal, validation and state-blending work every tick. The 60-trial rerun took about four minutes with three workers on the test VM, not counting setup. The workers run in independent processes and don't share memory. We didn't profile the engine or compare runtimes.
- **Scoring.** Goal-update damping is not a task lock. Candidate risk is a penalty, not a veto, and it is weighted by MetaMo's current state. Toy interest drops on every play tick, but curiosity drops only when a bout finishes. That interaction is a rule of this cat, not a general result about MetaMo.
