from instructor.models.simulation import Simulation
from __init__ import db, create_app
import json

app = create_app()
app.app_context().push()

sim = Simulation.query.get(70)

# Handle both dict and string
task_config = sim.task_config
if isinstance(task_config, str):
    task_config = json.loads(task_config)

print('Task Config Enabled:', task_config.get('enabled'))
print('Device Requirements:', len(task_config.get('device_requirements', [])))
print('Connection Requirements:', len(task_config.get('connection_requirements', [])))
print('CLI Devices:', len(task_config.get('cli_requirements', {})))
print('\nDevice Details:')
for dev in task_config.get('device_requirements', []):
    print(f'  - {dev.get("id")}: {dev.get("type")} ({dev.get("model")})')
print('\nCLI Commands:')
for device_id, commands in task_config.get('cli_requirements', {}).items():
    print(f'  {device_id}: {len(commands)} commands')
