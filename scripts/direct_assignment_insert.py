import os
import sys

# Ensure workspace root is on sys.path so we can import __init__.py
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from __init__ import create_app, db
from instructor.services.assignment_service import assignment_service
from instructor.models.simulation import Simulation
from instructor.models.class_model import Class

from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    try:
        sim = Simulation.query.first()
        if not sim:
            print("No simulations found. Cannot test.")
            raise SystemExit(2)
        cls = Class.query.first()
        if not cls:
            print("No classes found. Cannot test.")
            raise SystemExit(3)
        print(f"Using simulation_id={sim.id}, class_id={cls.id}")
        a = assignment_service.create_explicit_assignment(
            simulation_id=sim.id,
            class_id=cls.id,
            title=f"Direct Insert Test {datetime.utcnow().isoformat()}",
            description="Service-layer smoke test",
            max_attempts=3
        )
        print(f"SUCCESS: Created assignment id={a.id}")
    except Exception as e:
        import traceback
        print("ERROR during direct insert:", e)
        traceback.print_exc()
        raise
