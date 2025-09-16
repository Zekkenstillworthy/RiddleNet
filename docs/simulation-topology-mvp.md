# Simulation Topology MVP — Implementation Prompt

## Context
- Today, “configuration” for a simulation exists under `simulation.simulation_config`.
- Admin editor already writes a `network_topology` object into `simulation.simulation_config` (via edit/save routes).
- On the user side, `dynamic_simulation_routes.run_simulation` sends `simulation_data.topology = simulation.simulation_config` to the template.
- The user page (`templates/user/dynamic_simulation.html`) expects a topology at either:
  - `simulation.topology.devices|connections` or
  - `simulation.simulation_config.devices|connections`
- Because the actual data lives at `simulation.simulation_config.network_topology.*`, the topology isn’t surfaced properly in the user view.

Result: simulations can have configuration, but the topology doesn’t consistently appear for end users.

## Objective (MVP)
Ensure every simulation can have both a configuration and a topology, and that:
- Admin-defined `network_topology` is stored in the DB and retrievable.
- The user dynamic simulation loads and renders that topology.
- User changes to topology can be saved (per-attempt) and reloaded.

## Success Criteria
- Opening a published simulation with an admin-defined topology renders devices and connections on the user page.
- Saving topology from the user page persists to the active attempt and reloads after refresh.
- No breaking change for existing simulations that lack topology (UI degrades gracefully).

## Scope (MVP only)
1) Data shape alignment
- Canonical schema at `simulation.simulation_config.network_topology` with fields:
  - `devices`: array of `{ id: string, type: 'pc'|'switch'|'router'|..., label: string, interfaces?: [{ name: string, mac?: string }], ip?: string, subnet?: string, meta?: object }`
  - `connections` (aka `links`): array of `{ from: { deviceId: string, port: string }, to: { deviceId: string, port: string }, cable?: 'copper'|'fiber'|string, meta?: object }`
- Backward compatibility: if historical payloads used root-level `devices`/`connections`, keep supporting as a fallback.

2) Backend
- In `user/dynamic_simulation_routes.py::run_simulation`, set:
  - `simulation_data.topology = simulation.simulation_config.get('network_topology') or simulation.simulation_config`
  - Keep existing fallbacks for legacy fields.
- Provide a simple GET for topology (optional now if page already embeds data):
  - `GET /api/simulation/<id>/topology` → `{ devices, connections }` from `simulation_config.network_topology` with legacy fallbacks.
- Use the existing endpoint to persist per-attempt state:
  - `POST /dynamic-sim/api/simulation/<id>/network-state` with `{ topology, deviceStates }` writes into `SimulationAttempt.session_data.networkTopology`.

3) Frontend (user)
- In `templates/user/dynamic_simulation.html`:
  - Update `loadTopologyFromConfig()` to first try `simulation.topology` (new) → if missing, try `simulation.simulation_config.network_topology` → else fall back to any root-level `devices|connections|links`.
  - On Save Topology: continue saving to `localStorage` for instant UX, then also POST to `/dynamic-sim/api/simulation/<id>/network-state` with the topology payload.
  - On page load: if there’s an active attempt with `session_data.networkTopology`, prefer that to pre-fill the canvas.

4) Frontend (admin) — minimal
- No new UI required for MVP if current admin editor already emits `simulation_config.network_topology`.
- If missing, add a basic JSON-backed “Topology” panel in the editor that binds to `simulation_config.network_topology` (devices[], connections[]).

## Non-goals (MVP)
- Real-time multi-user topology sync and conflict resolution.
- Advanced device simulation/CLI emulation beyond current rules.
- Full topology validation engine (beyond basic existing checks and what’s already implemented).

## Acceptance Tests
- Admin creates/edits a simulation and sets `simulation_config.network_topology` with 2 PCs and 1 switch connected.
- User opens the simulation and sees the 3 devices and 2 links.
- User drags or adds/removes a device and clicks Save → on reload, the changed topology is restored from the attempt.
- Opening an older simulation without topology still loads and runs with no errors; topology area shows helper text.

## Edge Cases
- simulation_config is a stringified JSON → parse safely and fail soft.
- Empty or malformed `network_topology` → show hint and no crash.
- Legacy root-level `devices`/`connections` → still render via fallback.
- Attempt exists but has no `session_data.networkTopology` → fall back to admin-defined topology.

## Implementation Tasks

### Backend Changes
1. **Update topology mapping in `user/dynamic_simulation_routes.py::run_simulation`**:
   ```python
   # Current: simulation_data['topology'] = simulation_config
   # Enhanced:
   network_topology = simulation_config.get('network_topology', {})
   if network_topology and (network_topology.get('devices') or network_topology.get('connections')):
       simulation_data['topology'] = network_topology
   else:
       # Fallback to legacy root-level fields
       simulation_data['topology'] = simulation_config
   ```

2. **Add dedicated topology endpoint `GET /api/simulation/<id>/topology`**:
   - Returns canonical topology data with proper error handling
   - Supports both admin-defined and attempt-specific topology
   - Include validation and sanitization

3. **Enhance existing network-state endpoint validation**:
   - Validate topology structure before saving to `SimulationAttempt.session_data`
   - Add logging for topology operations
   - Handle malformed JSON gracefully

### Frontend Changes (User)
1. **Update `loadTopologyFromConfig()` in `templates/user/dynamic_simulation.html`**:
   ```javascript
   // Priority order: attempt data -> admin topology -> legacy fallbacks
   const attemptTopology = this.getAttemptTopology(); // from progress.session_data
   const adminTopology = this.simulation.topology; // from simulation_config.network_topology
   const legacyTopology = this.simulation.simulation_config; // fallback
   
   const topology = attemptTopology || adminTopology || legacyTopology;
   ```

2. **Enhance topology save flow**:
   - Immediate localStorage save for UX
   - Async POST to `/dynamic-sim/api/simulation/<id>/network-state`
   - Error handling and retry logic
   - Visual feedback for save status

3. **Add topology validation helpers**:
   - Client-side validation before save
   - Schema validation for devices and connections
   - Conflict detection for duplicate IDs

### Frontend Changes (Admin)
1. **Verify admin editor topology persistence**:
   - Ensure `simulation_config.network_topology` is properly written
   - Add validation for topology structure in admin forms
   - Preview capability for topology before publishing

### Error Handling & Validation
1. **Data validation patterns**:
   ```python
   def validate_topology_data(topology):
       if not isinstance(topology, dict):
           return False, "Topology must be an object"
       
       devices = topology.get('devices', [])
       connections = topology.get('connections', [])
       
       if not isinstance(devices, list) or not isinstance(connections, list):
           return False, "Devices and connections must be arrays"
       
       # Validate device structure
       for device in devices:
           if not device.get('id') or not device.get('type'):
               return False, "Each device must have id and type"
       
       return True, None
   ```

2. **Graceful degradation**:
   - Show helpful messages when topology is missing
   - Handle partial topology data (devices without connections)
   - Maintain backward compatibility with existing simulations

## Enhanced API Contracts

### GET Topology Endpoint
```
GET /api/simulation/<id>/topology
Headers: Authorization: Bearer <token>
Response: 200 OK
{
  "topology": {
    "devices": [
      {
        "id": "pc1",
        "type": "pc", 
        "label": "PC-1",
        "interfaces": [{"name": "eth0", "mac": "00:11:22:33:44:55"}],
        "ip": "192.168.1.10",
        "subnet": "255.255.255.0",
        "position": {"x": 100, "y": 150},
        "meta": {}
      }
    ],
    "connections": [
      {
        "id": "conn1",
        "from": {"deviceId": "pc1", "port": "eth0"},
        "to": {"deviceId": "switch1", "port": "port1"},
        "cable": "copper",
        "meta": {"bandwidth": "1Gbps"}
      }
    ]
  },
  "source": "admin|attempt|legacy",
  "lastModified": "2025-09-16T10:30:00Z"
}

Error responses:
404: {"error": "Simulation not found"}
403: {"error": "Access denied"}
400: {"error": "Invalid topology data"}
```

### Enhanced Network State Endpoint
```
POST /dynamic-sim/api/simulation/<id>/network-state
Headers: Content-Type: application/json
Request:
{
  "topology": {
    "devices": [...],
    "connections": [...]
  },
  "deviceStates": {
    "pc1": {"status": "configured", "config": {...}}
  },
  "metadata": {
    "action": "save|auto-save|submit",
    "timestamp": "2025-09-16T10:30:00Z"
  }
}

Response: 200 OK
{
  "success": true,
  "attemptId": 123,
  "lastUpdated": "2025-09-16T10:30:00Z",
  "validation": {
    "errors": [],
    "warnings": ["Device pc2 has no connections"]
  }
}
```

## Rollout/Guardrails
- Feature flag not required; safe by default.
- Log warnings when topology is missing or malformed to ease QA.
- No migration required; schema exists in JSON blob.

## Nice-to-haves (post-MVP)
- Basic topology diffing in attempt history.
- Server-side validation helpers to check incompatible links.
- Visual templates/snippets for common topologies in admin editor.

---

Summary: Wire up the user view to read from `simulation_config.network_topology`, persist per-attempt topology via the existing endpoint, and keep graceful fallbacks for legacy structures. This delivers “topology + configuration” end-to-end with minimal risk.
