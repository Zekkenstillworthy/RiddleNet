#!/usr/bin/env python3
"""
Simulation Assignment Management Tool

Features:
- List assignments with filters (class_id, title contains, active/published/available)
- Deactivate assignments (safe cleanup)
- Dry-run mode
- Non-interactive CLI args

Usage examples (Windows cmd):
  python scripts\sim_assignment_tool.py list
  python scripts\sim_assignment_tool.py list --class 9
  python scripts\sim_assignment_tool.py list --active --available
  python scripts\sim_assignment_tool.py clean --class 9 --dry-run
  python scripts\sim_assignment_tool.py clean --class 9 --yes
  python scripts\sim_assignment_tool.py clean --title "Static Routing" --yes

"""

import eventlet
eventlet.monkey_patch()

import argparse
import sys
import os
from datetime import datetime

# Add the project root to the path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from __init__ import create_app, db
from instructor.models.simulation_assignment import SimulationAssignment
from instructor.models.simulation import Simulation
from instructor.models.class_model import Class


def format_assignment(idx, a):
    sim_title = a.simulation.title if a.simulation else 'Unknown'
    return (
        f"{idx}. [{a.id}] {a.title} | sim='{sim_title}'\n"
        f"   class={a.class_id} module={a.module_id} type={a.assignment_type}\n"
        f"   active={'Y' if a.is_active else 'N'} published={'Y' if a.is_published else 'N'} available={'Y' if a.is_available else 'N'}"
    )


def matches_filters(a, args):
    if args.cls is not None and a.class_id != args.cls:
        return False
    # Only consider global assignments (no class) when requested
    if getattr(args, 'global_only', False) and a.class_id is not None:
        return False
    if args.title and args.title.lower() not in (a.title or '').lower() and (
        not a.simulation or args.title.lower() not in (a.simulation.title or '').lower()
    ):
        return False
    # Filter by assignment type (explicit, category, class, lesson, etc.)
    if getattr(args, 'atype', None):
        if (a.assignment_type or '').lower() != args.atype.lower():
            return False
    # Filter by simulation type
    if getattr(args, 'sim_type', None):
        if not a.simulation or (a.simulation.simulation_type or '').lower() != args.sim_type.lower():
            return False
    # Filter by simulation category
    if getattr(args, 'category', None):
        if not a.simulation or (a.simulation.category or '').lower() != args.category.lower():
            return False
    if args.active and not a.is_active:
        return False
    if args.published and not a.is_published:
        return False
    if args.available and not a.is_available:
        return False
    return True


def list_assignments(args):
    app = create_app()
    with app.app_context():
        q = SimulationAssignment.query
        items = q.all()
        filtered = [a for a in items if matches_filters(a, args)]
        print(f"Found {len(filtered)} assignment(s) matching filters out of {len(items)} total\n")
        for i, a in enumerate(filtered, 1):
            print(format_assignment(i, a))
        if args.summary:
            from collections import Counter
            by_class = Counter(a.class_id for a in filtered)
            print("\nSummary by class:")
            # Sort with None at the end
            for cid, count in sorted(by_class.items(), key=lambda kv: (kv[0] is None, kv[0] if kv[0] is not None else -1)):
                cname = None
                if cid is not None:
                    cls = Class.query.get(cid)
                    cname = getattr(cls, 'name', 'Unknown') if cls else 'Unknown'
                print(f"  Class {cid if cid is not None else 'None'} ({cname if cname else 'None'}): {count}")


def clean_assignments(args):
    app = create_app()
    with app.app_context():
        q = SimulationAssignment.query
        items = q.all()
        filtered = [a for a in items if matches_filters(a, args)]
        print(f"Cleaning {len(filtered)} assignment(s) (dry-run={args.dry_run}, delete={args.delete})\n")
        changed = 0
        for i, a in enumerate(filtered, 1):
            print(format_assignment(i, a))
            if not args.dry_run:
                if args.delete:
                    db.session.delete(a)
                    changed += 1
                else:
                    if a.is_active or a.is_available:
                        a.is_active = False
                        # available is computed; ensure windows are closed
                        a.available_from = datetime.utcnow()
                        a.available_until = datetime.utcnow()
                        changed += 1
        if not args.dry_run and changed:
            db.session.commit()
            verb = 'deleted' if args.delete else 'deactivated'
            print(f"\nCommitted: {verb} {changed} assignment(s)")
        elif args.dry_run:
            print("\nDry-run mode: no changes committed")


def make_parser():
    p = argparse.ArgumentParser(description='Simulation Assignment Tool')
    subs = p.add_subparsers(dest='cmd', required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('--class', dest='cls', type=int, help='Filter by class id')
    common.add_argument('--global-only', action='store_true', help='Only assignments not tied to any class (class_id is NULL)')
    common.add_argument('--title', type=str, help='Filter by title contains (assignment or simulation title)')
    common.add_argument('--type', dest='atype', type=str, help='Filter by assignment type (explicit, category, class, lesson)')
    common.add_argument('--sim-type', dest='sim_type', type=str, help='Filter by simulation type (e.g., "Networking 2")')
    common.add_argument('--category', type=str, help='Filter by simulation category (e.g., "Routing")')
    common.add_argument('--active', action='store_true', help='Only active')
    common.add_argument('--published', action='store_true', help='Only published')
    common.add_argument('--available', action='store_true', help='Only currently available')

    sp_list = subs.add_parser('list', parents=[common], help='List assignments')
    sp_list.add_argument('--summary', action='store_true', help='Show summary by class')

    sp_clean = subs.add_parser('clean', parents=[common], help='Deactivate matching assignments')
    sp_clean.add_argument('--dry-run', action='store_true', help='Preview changes without committing')
    sp_clean.add_argument('--yes', action='store_true', help='Confirm non-interactive (no prompt)')
    sp_clean.add_argument('--delete', action='store_true', help='Delete matching assignments instead of deactivating')

    return p


def main():
    parser = make_parser()
    args = parser.parse_args()

    if args.cmd == 'list':
        list_assignments(args)
    elif args.cmd == 'clean':
        if not args.yes and not args.dry_run:
            print('Refusing to modify without --yes or --dry-run')
            sys.exit(2)
        clean_assignments(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
