"""
LabLink Layer-2 Network Subsystem.

Provides MAC address abstractions, IEEE 802.1Q VLAN tag headers, Ethernet MAC framing,
deterministic software traffic generation, traffic sink sequence analysis, and performance metrics.
"""

from lablink.network.ethernet import TELEMETRY_PREFIX, EthernetFrame
from lablink.network.mac import BROADCAST_MAC, ZERO_MAC, MACAddress
from lablink.network.statistics import TrafficStatistics
from lablink.network.traffic import TrafficGenerator, TrafficSink
from lablink.network.vlan import VLANHeader

__all__ = [
    "BROADCAST_MAC",
    "TELEMETRY_PREFIX",
    "ZERO_MAC",
    "EthernetFrame",
    "MACAddress",
    "TrafficGenerator",
    "TrafficSink",
    "TrafficStatistics",
    "VLANHeader",
]
