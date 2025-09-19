import requests
import sys
from urllib.parse import urljoin

BASE = "http://127.0.0.1:5001"
LOGIN_URL = urljoin(BASE, "/admin/login")
LIST_URL = urljoin(BASE, "/admin/simulation/api/list")
ASSIGN_URL = urljoin(BASE, "/admin/simulation/api/assignments/explicit")

CLASS_ID = 7  # target class from user's report

s = requests.Session()

try:
    # 1) Login as admin (default credentials from setup: admin/admin)
    data = {"username": "admin", "password": "admin"}
    resp = s.post(LOGIN_URL, data=data, allow_redirects=False, timeout=10)
    print("Login status:", resp.status_code, resp.headers.get("Location"))
    if resp.status_code not in (200, 302):
        print("Login failed. Body:", resp.text[:500])
        sys.exit(1)

    # Follow redirect if present
    if resp.status_code == 302:
        loc = resp.headers.get("Location")
        if loc:
            s.get(urljoin(BASE, loc), timeout=10)

    # 2) Fetch simulations list
    resp = s.get(LIST_URL + "?include_inactive=false", timeout=15)
    print("List status:", resp.status_code)
    if resp.status_code != 200:
        print("Failed to list simulations:", resp.text[:500])
        sys.exit(1)

    data = resp.json()
    # Expected structure: {'simulations': [...]} or similar; be defensive
    sims = []
    if isinstance(data, dict):
        if "simulations" in data and isinstance(data["simulations"], list) and data["simulations"]:
            sims = data["simulations"]
        elif isinstance(data.get("items"), list) and data["items"]:
            sims = data["items"]
    if not sims:
        print("No simulations available to assign.")
        sys.exit(2)

    # Try to get an id field
    sim = sims[0]
    sim_id = sim.get("id") or sim.get("simulation", {}).get("id")
    if not sim_id:
        # some endpoints return objects with nested 'simulation'
        for cand in sims:
            sim_id = cand.get("id") or cand.get("simulation", {}).get("id")
            if sim_id:
                break
    if not sim_id:
        print("Couldn't determine a simulation id from list payload:", str(sim)[:200])
        sys.exit(3)

    # 3) Create explicit assignment
    payload = {
        "simulation_id": sim_id,
        "class_id": CLASS_ID,
        "title": f"Smoke Test Assignment for Simulation {sim_id}",
        "description": "Automated check via admin_assign_smoke_test.py",
        "max_attempts": 3
    }
    resp = s.post(ASSIGN_URL, json=payload, timeout=20)
    print("Assign status:", resp.status_code)
    print("Response:", resp.text)

    if resp.status_code != 200:
        sys.exit(4)
    res = resp.json()
    if not res.get("success"):
        sys.exit(5)
    print("SUCCESS: Assignment created with id:", res.get("assignment_id"))

except Exception as e:
    print("Smoke test error:", e)
    sys.exit(10)
