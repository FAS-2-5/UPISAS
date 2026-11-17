"""The challenge baseline: same scenario as run_challenge.py, but it never adapts.

Run it from the UPISAS folder: .venv\\Scripts\\python.exe ..\\challenge_tools\\run_baseline.py
"""
import os
import sys
import time

sys.path.insert(0, os.getcwd())
from UPISAS.exemplars.ramses import RAMSES

exemplar = RAMSES()
exemplar.start_run()
time.sleep(240)
exemplar.stop_container()
