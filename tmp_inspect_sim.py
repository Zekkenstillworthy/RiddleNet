from application import create_app
from instructor.controllers.simulation_controller import SimulationController
from instructor.routes.simulation_routes import TroubleshootingSimulation
import json

app = create_app()
app.app_context().push()

ctrl = SimulationController()
sim_data = ctrl.get_simulation_by_id(1, include_steps=True)
if 'simulation' not in sim_data:
    print(sim_data)
    raise SystemExit
simulation = sim_data['simulation']
sim_config = simulation.get('simulation_config')
print('raw type:', type(sim_config))
if isinstance(sim_config, str):
    sim_config = json.loads(sim_config)
print('parsed type:', type(sim_config))
print('keys:', list(sim_config.keys()))
network_topology = sim_config.get('network_topology')
print('network_topology raw type:', type(network_topology))
if isinstance(network_topology, str):
    network_topology = json.loads(network_topology)
print('network_topology keys:', list(network_topology.keys()) if isinstance(network_topology, dict) else 'N/A')
print('device count:', len(network_topology.get('devices', [])) if isinstance(network_topology, dict) else 'N/A')

def ensure_dict(d, key):
    val = d.get(key, {}) if isinstance(d, dict) else {}
    if isinstance(val, str):
        try:
            return json.loads(val) or {}
        except Exception:
            return {}
    return val if isinstance(val, dict) else {}

network_topology_via_helper = ensure_dict(sim_config, 'network_topology')
print('via ensure_dict count:', len(network_topology_via_helper.get('devices', [])))

troubleshooting_sim = TroubleshootingSimulation(
    id=simulation.get('id'),
    title=simulation.get('title'),
    initial_topology=network_topology,
    simulation_config=sim_config
)
ts_dict = troubleshooting_sim.to_dict()
print('TroubleshootingSimulation initial_topology devices:', len(ts_dict.get('initial_topology', {}).get('devices', [])))
