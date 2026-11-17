# Baseline runs (RAMSES scenario 1)

These are the baseline runs used in Section V of our Assignment 1 report.

## What was compared
| Configuration | What it does | Availability |
|---|---|---|
| No adaptation, run 1 | RAMSES runs the scenario and nothing adapts | 47.1% |
| No adaptation, run 2 | Same, a second run | 48.3% |
| Reactive baseline | Re-creates RAMSES's own "no instance left, start a new one" rule as a UPISAS strategy | 47.5% |

In scenario 1 the only `restaurant-service` instance is stopped 120 s into a 240 s run. RAMSES's own loop is switched off (`ADAPT=0`), so only the UPISAS strategy can adapt the system. In the reactive run, the replacement instance was not ready before the run ended, so availability did not recover.

## Files
- `my_strategy_reactive.py`: the reactive baseline strategy (a UPISAS `Strategy` subclass). `analyze()` checks whether `RESTAURANT-SERVICE` has no instance left; `plan()` adds one instance, with a 60 s cooldown.
- `run_baseline.py`: runs the scenario for 240 s without adapting.
- `run_reactive.py`: runs the scenario for 240 s with the reactive strategy, looping every 5 s.
- `measure_availability.py`: places one real order through the API gateway every second (create cart, add item, confirm order). A second counts as available only if all three steps succeed within 8 s. It also records which restaurant instances the probe sees every 2 s.
- `compare.sh`: starts a fresh RAMSES and runs the measurement next to a run script.
- `results/`: one JSON file per run, with the availability score, a per-second timeline and the instance list.
- `logs/`: the run, measurement and scenario logs of the latest baseline and reactive runs.

## Running them
The scripts were run from our local folder layout, where they lived in `challenge_tools/` next to the `UPISAS` folder and wrote results to `challenge_results/`. To run them again, put them back in that layout, or adjust the paths at the top of `measure_availability.py` and `compare.sh`. The RAMSES interface (`interface/interface.py`) must be running on port 50000.

To recount a result:
```bash
python -c "import json; d=json.load(open('baseline_runs/results/reactive-20261110-142412.json')); print(d['availability'])"
```

## Limits
These runs were measured with our own script, not Experiment Runner, and there is only one reactive run. Timing on a single laptop varies a lot between runs, so the numbers are an illustration rather than a precise measurement.
