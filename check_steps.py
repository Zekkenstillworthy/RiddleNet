import sqlite3
import json

conn = sqlite3.connect('instance/riddlenet.db')
cursor = conn.cursor()

print('=== SIMULATION 1 (User sees) ===')
cursor.execute('SELECT step_definitions FROM simulations WHERE id = 1')
step_data = cursor.fetchone()[0]
steps = json.loads(step_data)
print('Step 1:', json.dumps(steps[0], indent=2))

print('\n=== SIMULATION 61 (Admin created) ===')
cursor.execute('SELECT step_definitions FROM simulations WHERE id = 61')  
step_data = cursor.fetchone()[0]
steps = json.loads(step_data) 
print('Step 1:', json.dumps(steps[0], indent=2))

conn.close()
