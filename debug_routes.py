#!/usr/bin/env python3
"""Debug script to check registered routes"""
from run import app

print('=== All Registered Routes ===')
for rule in sorted(app.url_map.iter_rules(), key=lambda x: str(x.rule)):
    methods = list(rule.methods - {"HEAD", "OPTIONS"})
    print(f'{rule.rule:<40} -> {rule.endpoint} {methods}')

print('\n=== Looking for user/classes route ===')
user_routes = [rule for rule in app.url_map.iter_rules() if 'classes' in str(rule.rule)]
for rule in user_routes:
    methods = list(rule.methods - {"HEAD", "OPTIONS"})
    print(f'{rule.rule:<40} -> {rule.endpoint} {methods}')
