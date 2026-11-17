#!/bin/bash
# Runs the strategy and the baseline, each from a fresh RAMSES, and measures both.
# Run from Git Bash on Windows, with socat and interface/interface.py already running.
cd "$(dirname "$0")/../UPISAS" || exit 1
PY=.venv/Scripts/python.exe
TOOLS=../challenge_tools

fresh() {
  docker rm -f simulation-scenario >/dev/null 2>&1
  printf 'amd64\n\n' | wsl.exe -e bash -c 'cd "/mnt/c/Users/gupta/OneDrive/Desktop/FAS" && bash run_ramses.sh' 2>&1 \
    | tr -d '\000' | grep -E 'is ready|did not|DONE'
  echo "containers running: $(docker ps --format '{{.Names}}' | grep -cE '^(mysql|sefa-|ramses-)')"
}

measure() {
  label=$1; shift
  echo "=== $label: fresh RAMSES"
  fresh
  echo "=== $label: running"
  (until docker logs -f simulation-scenario > "$TOOLS/$label-scenario.log" 2>&1; do :; done) &
  logs=$!
  $PY -u $TOOLS/measure_availability.py "$label" > "$TOOLS/$label-measure.log" 2>&1 &
  meter=$!
  "$@" > "$TOOLS/$label-run.log" 2>&1
  wait $meter
  kill $logs 2>/dev/null
  cat "$TOOLS/$label-measure.log"
  grep -E 'Execute|already stopped' "$TOOLS/$label-run.log" | cut -c1-200
  grep -E 'injecting failure|Error while' "$TOOLS/$label-scenario.log" | cut -c1-160
  docker ps -a --format '{{.Names}}: {{.Status}}' | grep restaurant
}

# Usage: compare.sh [strategy label]. With a label, only the strategy runs, saved under that label.
# compare.sh all: spare (the submitted strategy), reactive and baseline, each from fresh.
if [ "$1" = "all" ]; then
  measure spare $PY -u run_challenge.py
  measure reactive $PY -u $TOOLS/run_reactive.py
  measure baseline $PY -u $TOOLS/run_baseline.py
elif [ -n "$1" ]; then
  measure "$1" $PY -u run_challenge.py
else
  measure strategy $PY -u run_challenge.py
  measure baseline $PY -u $TOOLS/run_baseline.py
fi
echo ALL_DONE
