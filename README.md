# Tater Tot · AGI 501

A Siberian Forest cat in a text-adventure version of Paxton's house. The house facts live in a MeTTa Atomspace (a store for symbolic facts). PeTTa runs the MeTTa code; MetaMo appraises the situation, scores possible actions, and picks one each tick. No LLM, API key, or network call is used during the simulation.

See [RESULTS.md](RESULTS.md) for the AGI 501 results and how to interpret them.

License: [MIT](LICENSE).

## Reproduce on Debian 12 (Linux)

Run from a fresh checkout of this repository:

```sh
sudo apt-get update
sudo apt-get install -y git curl build-essential cmake ninja-build pkg-config libgmp-dev libpcre2-dev zlib1g-dev python3-dev python3-numpy
bash setup.sh
python3 run.py --seed 1 --steps 200
python3 -m unittest discover -s tests -v
```

`setup.sh` checks out [PeTTa v1.0.2 (`429e22916630ea6fd1f24a3d45869f0082a85852`)](https://github.com/trueagi-io/PeTTa/tree/429e22916630ea6fd1f24a3d45869f0082a85852) and [MetaMo (`bf97e50a68aa5059457092dfbe70699b7dd1dbe2`)](https://github.com/iCog-Labs-Dev/MetaMo/tree/bf97e50a68aa5059457092dfbe70699b7dd1dbe2) under `.deps/`. It verifies the [SWI-Prolog 9.3.36 source archive](https://www.swi-prolog.org/download/devel/src/swipl-9.3.36.tar.gz) by SHA-256 and builds the interpreter there with Janus, its Python bridge. Tested with Python 3.11.2 and NumPy 1.24.2. No native PeTTa add-ons or MetaMo assistant dependencies are needed.

Run the unmodified [upstream trading example](https://github.com/iCog-Labs-Dev/MetaMo/tree/bf97e50a68aa5059457092dfbe70699b7dd1dbe2/usecase/metamo-trading-agent):

```sh
root=$PWD
mkdir -p runs
(cd .deps/MetaMo/usecase/metamo-trading-agent && PATH="$root/.deps/swi/bin:$PATH" LC_ALL=C.UTF-8 sh "$root/.deps/PeTTa/run.sh" trading_agent.metta --silent) > runs/trading.log
grep 'TRADER FINAL' runs/trading.log
```

After installing the Debian packages above, rerun the final-report matrix (60 trials). The script calls `setup.sh` if the toolchain is missing:

```sh
python3 experiments.py --jobs 3
```

Read `runs/experiments/summary.md` and find individual CSV and JSON files in the condition subdirectories.

Each run writes `runs/<mode>-<seed>-<steps>.csv` and a JSON summary with the same stem. The CSV records end-of-tick room and drives, Paxton's room, action (`move` if traveling), chosen task and its goal, prior task, work counts, glass status, health, fear, the candle candidate's risk before the action, and whether the adapter allows the interruption of an unfinished task (`allowed_interruption`). `work=0` after a non-move action means the task completed. `--out` changes the destination. Identical seeds replay the same schedule of Paxton's room choices across conditions. Non-default flags add a suffix to the mode in the output filename. The JSON `bouts` field gives the count, total work ticks and mean length per drive. A bout starts at the first work tick and ends at completion or a switch; the measured part of a bout still open at the last tick is included. Travel does not count.

Use `--damping off` to bypass only MetaMo's homeostatic damping (which shrinks goal updates near an internal safety boundary). It still checks stability, blends states, and projects back into the safe region. Use `--naps off` to remove sleep from the menu and hold tiredness at zero, including for appraisal. Both switches default to `on`.

Use `--memory on` to recall scoldings when scoring the knock candidate, and `--novelty off` to remove the candidate's novelty-goal (`gNovel`) contribution without disabling curiosity or toy interest. Use `--bag-tick 100` or `--candle-tick 100` to enable the corresponding prop from tick 100. Heat and short-lived fear count even with recall off; `--candle-memory on` adds remembered singes independently of scolding recall. Both prop arrivals and both types of recall are off by default.

## How it works

- [House](sim/house.metta): four rooms with the hallway as the hub. Paxton can change rooms every seven ticks. The food bowl is in the kitchen; the litter box is in the hallway. The glass falls to the floor and resets every twelve ticks; Paxton scolds if present when it falls.
- [Cat](sim/cat.metta): six drives rise each tick and drop on task completion. Each toy loses interest during play and recovers when left alone. Travel takes time but doesn't count as work on a task.
- [Sleep and litter](sim/body.metta): tiredness rises **2 points per tick** and resets to zero after **6 work ticks** of sleep in the bedroom. Litter need rises **3 points per tick**, or **8 per tick for the next 5 ticks after finishing a meal**. It resets to zero after **2 work ticks** at the litter box. Both start at zero and cap at 100.
- [Adapter](sim/adapter.metta): following the trading example, world observations become one stimulus (novelty, conduciveness or how favorable things look, risk, effort) and a menu of actions with goal correlations (how much each action helps each MetaMo goal). The highest of hunger, tiredness, and litter need makes the situation look less favorable as it rises. Sleep and litter use the same MetaMo goals as eating (`gHelp` and `gSelf`): they help Tater Tot take care of herself. The [loop](sim/run.metta) runs the default MetaMo cycle with one subsystem, executes its chosen action, then keeps the returned motivational state. The six drive meters are separate from that internal state. There is no fallback picker.
- [Q1 measurement](run.py): a flip-flop is a change away from an unfinished task **after work has started**. Leaving any task for litter, or leaving a curiosity task (including inspecting the candle) or sleep for food, is allowed. The summary separates goal changes from switches between toys (same goal), and counts travel replans, play-to-eat switches, and litter interruptions separately. Any switch out of a started, unfinished nap also counts as waking early, even if allowed. `finish` narrows the menu once work has started but keeps those allowed alternatives available to MetaMo. It does not lock in travel plans.
- [Reward + attention](sim/feedback.metta): `--mode reward-attention` keeps the whole menu. Work captures attention, which then decays. Drive relief gives the task a short-lived reward. The adapter translates both into changes in each candidate's goal correlations (how useful the action looks to MetaMo). MetaMo still picks every action using its regular appraisal, risk scoring and damping. `baseline` is still the default.
