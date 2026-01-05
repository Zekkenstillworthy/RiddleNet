"""Canonical Link Up! challenge definitions shared across backend layers."""
from __future__ import annotations

from typing import Iterable, List, Dict

# Foundation phase definitions (Phase -> ordered module ids)
LINKUP_FOUNDATION_PHASES: Dict[int, List[str]] = {
    1: ["meet-pc", "meet-switch", "meet-router"],
    2: ["pc-to-pc", "pc-to-switch", "switch-to-router"],
    3: ["small-office", "home-network", "network-expansion"],
    4: ["point-to-point-topology", "bus-topology", "star-topology"],
    5: ["ring-topology", "tree-topology", "mesh-topology", "hybrid-topology"],
}

LINKUP_FOUNDATION_ORDER: List[str] = [
    module_id
    for phase in sorted(LINKUP_FOUNDATION_PHASES)
    for module_id in LINKUP_FOUNDATION_PHASES[phase]
]
LINKUP_FOUNDATION_TOTAL: int = len(LINKUP_FOUNDATION_ORDER)
LINKUP_FOUNDATION_SET = set(LINKUP_FOUNDATION_ORDER)

LINKUP_ADVANCED_CHALLENGES: Dict[str, List[str]] = {
    "easy": ["vlan-basics", "default-gateway", "dhcp-client"],
    "intermediate": ["extended-ring-redundancy", "hybrid-star-ring", "partial-mesh-ospf"],
    "hard": ["mpls-vpn-complex", "datacenter-fabric", "sd-wan-overlay"],
}
LINKUP_ADVANCED_SETS = {key: set(values) for key, values in LINKUP_ADVANCED_CHALLENGES.items()}

_DUPLICATE_ALIASES = {
    "default-gateway-setup": "default-gateway",
    "default_gateway_setup": "default-gateway",
    "default_gateway": "default-gateway",
    "dhcp-client-config": "dhcp-client",
    "dhcp_client_config": "dhcp-client",
    "dhcp_client": "dhcp-client",
}


def _build_alias_registry() -> Dict[str, str]:
    registry: Dict[str, str] = {}

    def _register(canonical: str, *aliases: str) -> None:
        normalized = canonical.lower()
        registry[normalized] = canonical
        registry[normalized.replace("-", "_")] = canonical
        registry[normalized.replace("_", "-")] = canonical
        for alias in aliases:
            alias_key = str(alias).strip().lower()
            registry[alias_key] = canonical
            registry[alias_key.replace("-", "_")] = canonical
            registry[alias_key.replace("_", "-")] = canonical

    for idx, module_id in enumerate(LINKUP_FOUNDATION_ORDER, start=1):
        _register(
            module_id,
            f"foundation-{module_id}",
            f"{module_id}-module",
            f"foundation_{module_id}",
            f"module-{module_id}",
            str(idx),
        )

    for difficulty, challenge_ids in LINKUP_ADVANCED_CHALLENGES.items():
        for challenge_id in challenge_ids:
            _register(challenge_id, f"{difficulty}-{challenge_id}")

    for alias, canonical in _DUPLICATE_ALIASES.items():
        _register(canonical, alias)

    return registry

_LINKUP_ALIAS_REGISTRY = _build_alias_registry()


def normalize_linkup_id(raw_id) -> str | None:
    """Return canonical module id for any known Link Up! identifier."""
    if raw_id is None:
        return None

    if isinstance(raw_id, (int, float)):
        key = str(int(raw_id))
    else:
        key = str(raw_id).strip()

    key_lower = key.lower()
    key_lower = key_lower.replace(" ", "-")
    key_lower = key_lower.replace("--", "-")
    candidate = _LINKUP_ALIAS_REGISTRY.get(key_lower)
    if candidate:
        return candidate

    alt_key = key_lower.replace("-", "_")
    candidate = _LINKUP_ALIAS_REGISTRY.get(alt_key)
    if candidate:
        return candidate

    alt_key = key_lower.replace("_", "-")
    candidate = _LINKUP_ALIAS_REGISTRY.get(alt_key)
    if candidate:
        return candidate

    return None


def canonicalize_completed_ids(raw_ids: Iterable) -> List[str]:
    """Deduplicate and normalize completed challenge ids while preserving order."""
    seen = set()
    canonical_list: List[str] = []
    for raw_id in raw_ids:
        canonical = normalize_linkup_id(raw_id)
        if not canonical or canonical in seen:
            continue
        canonical_list.append(canonical)
        seen.add(canonical)
    return canonical_list


def calculate_linkup_counts(canonical_ids: Iterable[str]) -> Dict[str, int]:
    """Calculate per-category completion counts from canonical ids."""
    foundation_count = 0
    easy_count = 0
    intermediate_count = 0
    hard_count = 0

    for cid in canonical_ids:
        if cid in LINKUP_FOUNDATION_SET:
            foundation_count += 1
        elif cid in LINKUP_ADVANCED_SETS["easy"]:
            easy_count += 1
        elif cid in LINKUP_ADVANCED_SETS["intermediate"]:
            intermediate_count += 1
        elif cid in LINKUP_ADVANCED_SETS["hard"]:
            hard_count += 1

    return {
        "foundation": min(foundation_count, LINKUP_FOUNDATION_TOTAL),
        "easy": min(easy_count, len(LINKUP_ADVANCED_CHALLENGES["easy"])),
        "intermediate": min(intermediate_count, len(LINKUP_ADVANCED_CHALLENGES["intermediate"])),
        "hard": min(hard_count, len(LINKUP_ADVANCED_CHALLENGES["hard"])),
        "total": min(foundation_count, LINKUP_FOUNDATION_TOTAL),
        "required": LINKUP_FOUNDATION_TOTAL,
    }


def is_foundation_module(module_id: str | None) -> bool:
    """Return True when the canonical module id belongs to the foundation set."""
    return bool(module_id) and module_id in LINKUP_FOUNDATION_SET
