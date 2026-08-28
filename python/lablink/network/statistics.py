"""
LabLink Layer-2 Network Traffic Statistics Model.

Provides structured statistics telemetry for packet counts, byte counts,
sequence loss metrics, duplicate detection, throughput rates, and latency measurements.
"""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class TrafficStatistics:
    """
    Structured representation of Layer-2 traffic execution results and performance metrics.
    """

    transmitted_packets: int = 0
    received_packets: int = 0
    transmitted_bytes: int = 0
    received_bytes: int = 0
    lost_packets: int = 0
    duplicate_packets: int = 0
    corrupted_packets: int = 0
    duration_sec: float = 0.0
    throughput_bytes_per_sec: float = 0.0
    throughput_bits_per_sec: float = 0.0
    throughput_packets_per_sec: float = 0.0
    packet_loss_percentage: float = 0.0
    min_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    mean_latency_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Return dictionary dictionary representation of traffic statistics."""
        return asdict(self)
