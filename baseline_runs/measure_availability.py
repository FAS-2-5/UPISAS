"""Measures ORDERING-SERVICE availability during one 4-minute challenge run.

Waits for the simulation-scenario container, then for 240 s places one real order
per second through the API gateway (create cart, add item, confirm). A second counts
as available when the whole order succeeds. Saves a timeline to challenge_results/.

Usage: measure_availability.py <label>
"""
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import requests

DURATION = 240
TIMEOUT = 8
PROBE = "http://localhost:55010/rest/systemArchitecture"
RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "challenge_results")


def docker(*args):
    return subprocess.run(["docker", *args], capture_output=True, text=True).stdout.strip()


def gateway():
    return "http://localhost:" + docker("port", "sefa-api-gateway", "58081/tcp").splitlines()[0].rsplit(":", 1)[1]


def order(base, restaurant_id, item_id):
    try:
        r = requests.post(f"{base}/customer/cart/", json={"restaurantId": restaurant_id}, timeout=TIMEOUT)
        r.raise_for_status()
        cart = r.json()["id"]
        r = requests.post(f"{base}/customer/cart/{cart}/addItem", timeout=TIMEOUT, json={
            "cartId": cart, "restaurantId": restaurant_id, "itemId": item_id, "quantity": 2})
        r.raise_for_status()
        if len(r.json().get("items", [])) != 1:
            return False, "wrong items"
        r = requests.post(f"{base}/customer/cart/{cart}/confirmOrder", timeout=TIMEOUT, json={
            "cartId": cart, "cardNumber": "1111111111111111", "expMonth": 12, "expYear": 2023, "cvv": "001",
            "address": "Via REST Client", "city": "Roma", "number": 1, "zipcode": "12345",
            "telephoneNumber": "1234567890", "scheduledTime": int(time.time() * 1000)})
        r.raise_for_status()
        return True, ""
    except (requests.RequestException, ValueError, KeyError) as e:
        return False, type(e).__name__ + ":" + str(getattr(getattr(e, "response", None), "status_code", ""))


def restaurant_instances():
    try:
        architecture = requests.get(PROBE, timeout=5).json()
        return architecture.get("RESTAURANT-SERVICE", {}).get("instances", [])
    except (requests.RequestException, ValueError):
        return None


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "run"
    base = gateway()
    restaurants = requests.get(f"{base}/customer/restaurants", timeout=20).json()["restaurants"]
    restaurant_id = restaurants[0]["id"]
    menu = requests.get(f"{base}/customer/restaurants/{restaurant_id}/menu", timeout=20).json()
    item_id = menu["menuItems"][0]["id"]
    print(f"gateway {base}, restaurant {restaurant_id}, item {item_id}; waiting for scenario", flush=True)

    while docker("inspect", "-f", "{{.State.Status}}", "simulation-scenario") != "running":
        time.sleep(0.5)

    start = time.monotonic()
    print("scenario running, measuring", flush=True)
    pending, instances = [], []
    with ThreadPoolExecutor(max_workers=40) as pool:
        for second in range(DURATION):
            pending.append((second, pool.submit(order, base, restaurant_id, item_id)))
            if second % 2 == 0:
                instances.append((second, pool.submit(restaurant_instances)))
            time.sleep(max(0, start + second + 1 - time.monotonic()))

    timeline = [{"t": s, "ok": f.result()[0], "error": f.result()[1]} for s, f in pending]
    instance_log = [{"t": s, "instances": f.result()} for s, f in instances]
    ok = sum(entry["ok"] for entry in timeline)
    availability = ok / DURATION

    failed = [entry["t"] for entry in timeline if not entry["ok"]]
    os.makedirs(RESULTS, exist_ok=True)
    path = os.path.join(RESULTS, f"{label}-{datetime.now():%Y%m%d-%H%M%S}.json")
    with open(path, "w") as out:
        json.dump({"label": label, "availability": availability, "timeline": timeline, "instances": instance_log}, out)

    print(f"\n{label}: availability {availability:.1%} ({ok}/{DURATION} s)")
    print(f"first failure t={failed[0] if failed else '-'}, last failure t={failed[-1] if failed else '-'}, failed seconds={len(failed)}")
    changes, previous = [], "?"
    for entry in instance_log:
        if entry["instances"] != previous:
            changes.append(entry)
            previous = entry["instances"]
    print("restaurant instances over time:")
    for entry in changes:
        print(f"  t={entry['t']:3d}s {entry['instances']}")
    print("saved", path)


if __name__ == "__main__":
    main()
