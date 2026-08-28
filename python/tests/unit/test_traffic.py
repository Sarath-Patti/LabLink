"""
Unit tests for TrafficGenerator, TrafficSink, and TrafficStatistics analysis.
"""

from lablink.network.statistics import TrafficStatistics
from lablink.network.traffic import TrafficGenerator, TrafficSink


def test_traffic_generator_batch_creation() -> None:
    """Verify TrafficGenerator creates exact frame count with correct padding."""
    gen = TrafficGenerator(
        src_mac="00:11:22:33:44:55",
        dst_mac="00:AA:BB:CC:DD:EE",
        vlan_id=100,
        frame_size=64,
        packet_count=10,
    )
    frames = gen.generate_frames()

    assert len(frames) == 10
    for i, frame in enumerate(frames, start=1):
        assert frame.sequence_number == i
        assert frame.frame_size >= 64
        assert frame.vlan_header is not None
        assert frame.vlan_header.vlan_id == 100


def test_traffic_sink_analysis_and_statistics() -> None:
    """Verify TrafficSink ingests frames and computes accurate TrafficStatistics."""
    gen = TrafficGenerator(
        src_mac="00:11:22:33:44:55",
        dst_mac="00:AA:BB:CC:DD:EE",
        frame_size=64,
        packet_count=20,
    )
    frames = gen.generate_frames()

    sink = TrafficSink()
    tx_bytes = sum(f.frame_size for f in frames)

    # Process first 18 frames (simulate 2 dropped frames)
    for frame in frames[:18]:
        sink.process_frame(frame)

    stats = sink.analyze(transmitted_count=20, transmitted_bytes=tx_bytes, duration_sec=1.0)

    assert isinstance(stats, TrafficStatistics)
    assert stats.transmitted_packets == 20
    assert stats.received_packets == 18
    assert stats.lost_packets == 2
    assert stats.packet_loss_percentage == 10.0
    assert stats.throughput_packets_per_sec == 18.0
    assert stats.throughput_bytes_per_sec > 0.0
    assert stats.throughput_bits_per_sec > 0.0


def test_traffic_sink_duplicate_and_corrupted_handling() -> None:
    """Verify duplicate frame and corrupted byte sequence handling."""
    gen = TrafficGenerator(
        src_mac="00:11:22:33:44:55",
        dst_mac="00:AA:BB:CC:DD:EE",
        packet_count=2,
    )
    frames = gen.generate_frames()

    sink = TrafficSink()
    sink.process_frame(frames[0])
    sink.process_frame(frames[0])  # Duplicate
    sink.process_bytes(b"TRUNCATED")  # Truncated corrupted bytes (< 14 bytes)

    stats = sink.analyze(transmitted_count=2, transmitted_bytes=128, duration_sec=1.0)

    assert stats.duplicate_packets == 1
    assert stats.corrupted_packets == 1
