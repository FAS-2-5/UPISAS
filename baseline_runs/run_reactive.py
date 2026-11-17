"""Same loop as run_challenge.py, but with the earlier reactive strategy (my_strategy_reactive.py).

Run it from the UPISAS folder: .venv\\Scripts\\python.exe ..\\challenge_tools\\run_reactive.py
"""
import importlib.util
import os
import sys
import time

sys.path.insert(0, os.getcwd())
from UPISAS.exemplars.ramses import RAMSES

spec = importlib.util.spec_from_file_location(
    "my_strategy_reactive", os.path.join(os.path.dirname(os.path.abspath(__file__)), "my_strategy_reactive.py"))
reactive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reactive)

exemplar = RAMSES()
strategy = reactive.MyStrategy(exemplar)
exemplar.start_run()

start = time.monotonic()
while time.monotonic() - start < 240:
    try:
        strategy.monitor(with_validation=False)
        if strategy.analyze() and strategy.plan():
            strategy.execute(strategy.knowledge.plan_data, with_validation=False)
    except Exception as e:
        print(e)
    time.sleep(5 - (time.monotonic() - start) % 5)

exemplar.stop_container()
