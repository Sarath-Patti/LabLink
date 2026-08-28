"""
Performance Test Suite for Layer-2 Ethernet Serialization, Parsing, and Traffic Generation.
"""

import pytest

from lablink.network.ethernet import EthernetFrame
from lablink.network.traffic import TrafficGenerator
from lablink.network.vlan import VLANHeader
from tests.utilities.assertions import assert_greater_than, assert_less_than
from tests.utilities.helpers import measure_execution_time


@pytest.mark.l2
@pytest.mark.performance
def test_ethernet_frame_serialization_performance() -> None:
    """Benchmark EthernetFrame binary serialization speed over 1,000 iterations."""
    frame = EthernetFrame(
        dst_mac="00:AA:BB:CC:DD:EE",
        src_mac="00:11:22:33:44:55",
        vlan_header=VLANHeader(100),
        payload=b"BENCHMARK_PAYLOAD_DATA",
    )

    def serialize_loop() -> None:
        for _ in range(1000):
            _ = frame.to_bytes()

    _, duration = measure_execution_time(serialize_loop)
    rate_fps = 1000.0 / duration if duration > 0 else 1e6

    assert_greater_than(rate_fps, 5000.0, "Serialization rate below performance target")


@pytest.mark.l2
@pytest.mark.performance
def test_ethernet_frame_parsing_performance() -> None:
    """Benchmark EthernetFrame binary parsing speed over 1,000 iterations."""
    raw_bytes = EthernetFrame(
        dst_mac="00:AA:BB:CC:DD:EE",
        src_mac="00:11:22:33:44:55",
        vlan_header=VLANHeader(100),
        payload=b"BENCHMARK_PAYLOAD_DATA",
    ).to_bytes()

    def parse_loop() -> None:
        for _ in range(1000):
            _ = EthernetFrame.from_bytes(raw_bytes)

    _, duration = measure_execution_time(parse_loop)
    rate_fps = 1000.0 / duration if duration > 0 else 1e6

    assert_greater_than(rate_fps, 5000.0, "Parsing rate below performance target")


@pytest.mark.l2
@pytest.mark.performance
def test_traffic_generator_batch_performance() -> None:
    """Benchmark TrafficGenerator batch creation performance for 2,000 frames."""
    gen = TrafficGenerator(
        src_mac="00:11:22:33:44:55",
        dst_mac="00:AA:BB:CC:DD:EE",
        vlan_id=100,
        packet_count=2000,
    )

    _, duration = measure_execution_time(gen.generate_frames)
    assert_less_than(duration, 2.0, "Batch traffic generation exceeded duration threshold")
