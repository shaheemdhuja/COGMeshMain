"""Deterministic weighted scoring engine evaluating edge node suitability for task assignment."""

from typing import List, Optional, Tuple
from app.models.capability import Capability
from app.models.device import Device

# Weight Constants (Tunable parameters for adaptive scheduling)
CAPABILITY_MATCH_WEIGHT: float = 0.35
BATTERY_WEIGHT: float = 0.20
RAM_WEIGHT: float = 0.20
CPU_WEIGHT: float = 0.15
NETWORK_WEIGHT: float = 0.10


class SchedulingScore:
    """Calculates suitability score for an edge device given task requirements and node telemetry."""

    @classmethod
    def calculate_score(
        cls,
        device: Device,
        capability: Optional[Capability],
        required_capabilities: List[str],
    ) -> Tuple[float, str]:
        """Calculate weighted score in range [0.0, 1.0] and return score with detailed breakdown reason.
        
        Returns (0.0, reason) if device fails hard eligibility rules.
        """
        # Hard Rule 1: Device must be ONLINE or READY
        if device.status.upper() not in ["ONLINE", "READY"]:
            return 0.0, f"Device status is '{device.status}' (must be ONLINE or READY)"

        # Hard Rule 2: Capability snapshot must exist
        if not capability:
            return 0.0, "No capability snapshot registered for device"

        # Hard Rule 3: Required capabilities must be supported by device
        supported_set = set(task.upper() for task in (capability.supported_tasks or []))
        for req in required_capabilities:
            if req.upper() not in supported_set:
                return 0.0, f"Device lacks required capability '{req}'"

        # Normalize factors to [0.0, 1.0] range
        cap_score = 1.0
        battery_score = min(max(capability.battery_level / 100.0, 0.0), 1.0)
        ram_score = min(max(capability.ram_gb / 32.0, 0.0), 1.0)
        cpu_score = min(max(capability.cpu_cores / 16.0, 0.0), 1.0)

        net_str = capability.network_quality.upper() if capability.network_quality else "GOOD"
        net_map = {"EXCELLENT": 1.0, "GOOD": 0.8, "FAIR": 0.5, "POOR": 0.2}
        network_score = net_map.get(net_str, 0.5)

        # Weighted calculation
        total_score = (
            (CAPABILITY_MATCH_WEIGHT * cap_score)
            + (BATTERY_WEIGHT * battery_score)
            + (RAM_WEIGHT * ram_score)
            + (CPU_WEIGHT * cpu_score)
            + (NETWORK_WEIGHT * network_score)
        )

        reason = (
            f"Selected with weighted score {total_score:.3f} "
            f"(Battery: {capability.battery_level}%, RAM: {capability.ram_gb}GB, "
            f"CPU: {capability.cpu_cores} cores, Network: {net_str})"
        )

        return round(total_score, 4), reason
