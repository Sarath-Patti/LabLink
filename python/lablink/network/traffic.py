"""
LabLink Software Traffic Generator and Traffic Receiver/Sink Engine.

Provides deterministic Layer-2 Ethernet frame generation, sequence tracking,
missing frame detection, duplicate frame analysis, and performance metrics computation.
"""

import time

from lablink.exceptions import MalformedFrameError
from lablink.logging import get_logger
from lablink.network.ethernet import EthernetFrame
from lablink.network.mac import MACAddress
from lablink.network.statistics import TrafficStatistics
from lablink.network.vlan import VLANHeader

logger = get_logger("network.traffic")


class TrafficGenerator:
    """
    Deterministic software Layer-2 Ethernet frame generator.
    """

    def __init__(
        self,
        src_mac: MACAddress | str,
        dst_mac: MACAddress | str,
        ethertype: int = 0x0800,
        vlan_id: int | None = None,
        frame_size: int = 64,
        packet_count: int = 100,
        rate_fps: float = 1000.0,
    ) -> None:
        self.src_mac: MACAddress = (
            src_mac if isinstance(src_mac, MACAddress) else MACAddress(src_mac)
        )
        self.dst_mac: MACAddress = (
            dst_mac if isinstance(dst_mac, MACAddress) else MACAddress(dst_mac)
        )
        self.ethertype: int = ethertype
        self.vlan_id: int | None = vlan_id
        self.frame_size: int = max(64, frame_size)
        self.packet_count: int = max(1, packet_count)
        self.rate_fps: float = max(1.0, rate_fps)

    def generate_frame(
        self, sequence_number: int, timestamp_ns: int | None = None
    ) -> EthernetFrame:
        """
        Generate a single EthernetFrame with embedded telemetry and requested frame size.

        Args:
            sequence_number: 1-indexed sequence number.
            timestamp_ns: Optional generation timestamp in nanoseconds.

        Returns:
            Populated EthernetFrame object.
        """
        vlan = VLANHeader(vlan_id=self.vlan_id) if self.vlan_id is not None else None
        frame = EthernetFrame(
            dst_mac=self.dst_mac,
            src_mac=self.src_mac,
            ethertype=self.ethertype,
            vlan_header=vlan,
        )

        # Embed telemetry header
        frame.embed_telemetry(sequence_number, timestamp_ns=timestamp_ns)

        # Pad payload to meet target frame size
        current_len = len(frame.to_bytes())
        if current_len < self.frame_size:
            pad_needed = self.frame_size - current_len
            frame.payload += b"\x00" * pad_needed

        return frame

    def generate_frames(self) -> list[EthernetFrame]:
        """
        Generate all configured frames deterministically in batch.

        Returns:
            List of generated EthernetFrame objects.
        """
        logger.debug(f"Generating {self.packet_count} frames (target size={self.frame_size}B)...")
        return [self.generate_frame(seq) for seq in range(1, self.packet_count + 1)]

    def run(self) -> list[EthernetFrame]:
        """Alias for generate_frames."""
        return self.generate_frames()


class TrafficSink:
    """
    Software Layer-2 Ethernet frame receiver and analyzer.
    """

    def __init__(self) -> None:
        self.received_frames: list[EthernetFrame] = []
        self.received_sequences: list[int] = []
        self.duplicate_count: int = 0
        self.corrupted_count: int = 0
        self.latencies_ms: list[float] = []
        self.first_rx_timestamp_ns: int | None = None
        self.last_rx_timestamp_ns: int | None = None

    def reset(self) -> None:
        """Reset internal receiver metrics and frame collections."""
        self.received_frames.clear()
        self.received_sequences.clear()
        self.duplicate_count = 0
        self.corrupted_count = 0
        self.latencies_ms.clear()
        self.first_rx_timestamp_ns = None
        self.last_rx_timestamp_ns = None

    def process_frame(self, frame: EthernetFrame, rx_timestamp_ns: int | None = None) -> None:
        """
        Process an ingested EthernetFrame and update sequence/timing telemetry.

        Args:
            frame: Ingested EthernetFrame object.
            rx_timestamp_ns: Optional receive timestamp in nanoseconds.
        """
        now_ns = rx_timestamp_ns if rx_timestamp_ns is not None else time.time_ns()

        if self.first_rx_timestamp_ns is None:
            self.first_rx_timestamp_ns = now_ns
        self.last_rx_timestamp_ns = now_ns

        if frame.sequence_number is not None:
            if frame.sequence_number in self.received_sequences:
                self.duplicate_count += 1
            else:
                self.received_sequences.append(frame.sequence_number)

        if frame.timestamp_ns is not None and now_ns >= frame.timestamp_ns:
            latency_ms = (now_ns - frame.timestamp_ns) / 1e6
            self.latencies_ms.append(latency_ms)

        self.received_frames.append(frame)

    def process_bytes(self, raw_data: bytes, rx_timestamp_ns: int | None = None) -> None:
        """
        Parse raw bytes and process resulting EthernetFrame.

        Args:
            raw_data: Raw binary MAC frame bytes.
            rx_timestamp_ns: Optional receive timestamp in nanoseconds.
        """
        try:
            frame = EthernetFrame.from_bytes(raw_data)
            self.process_frame(frame, rx_timestamp_ns=rx_timestamp_ns)
        except MalformedFrameError:
            self.corrupted_count += 1
            logger.warning(f"TrafficSink received corrupted frame ({len(raw_data)} bytes).")

    def analyze(
        self,
        transmitted_count: int,
        transmitted_bytes: int,
        duration_sec: float = 0.0,
    ) -> TrafficStatistics:
        """
        Compute comprehensive traffic execution statistics.

        Args:
            transmitted_count: Total frames transmitted by generator.
            transmitted_bytes: Total bytes transmitted by generator.
            duration_sec: Optional manual execution duration override in seconds.

        Returns:
            TrafficStatistics instance populated with metrics.
        """
        rx_count = len(self.received_frames)
        rx_bytes = sum(f.frame_size for f in self.received_frames)

        if self.received_sequences:
            unique_received = len(set(self.received_sequences))
            lost_packets = max(0, transmitted_count - unique_received)
        else:
            lost_packets = max(0, transmitted_count - rx_count)

        loss_pct = (lost_packets / transmitted_count * 100.0) if transmitted_count > 0 else 0.0

        # Determine test duration
        if duration_sec > 0:
            dur = duration_sec
        elif (
            self.first_rx_timestamp_ns
            and self.last_rx_timestamp_ns
            and self.last_rx_timestamp_ns > self.first_rx_timestamp_ns
        ):
            dur = (self.last_rx_timestamp_ns - self.first_rx_timestamp_ns) / 1e9
        else:
            dur = 0.001

        tp_bytes_sec = rx_bytes / dur
        tp_bits_sec = (rx_bytes * 8) / dur
        tp_packets_sec = rx_count / dur

        min_lat = min(self.latencies_ms) if self.latencies_ms else 0.0
        max_lat = max(self.latencies_ms) if self.latencies_ms else 0.0
        mean_lat = (sum(self.latencies_ms) / len(self.latencies_ms)) if self.latencies_ms else 0.0

        return TrafficStatistics(
            transmitted_packets=transmitted_count,
            received_packets=rx_count,
            transmitted_bytes=transmitted_bytes,
            received_bytes=rx_bytes,
            lost_packets=lost_packets,
            duplicate_packets=self.duplicate_count,
            corrupted_packets=self.corrupted_count,
            duration_sec=dur,
            throughput_bytes_per_sec=tp_bytes_sec,
            throughput_bits_per_sec=tp_bits_sec,
            throughput_packets_per_sec=tp_packets_sec,
            packet_loss_percentage=loss_pct,
            min_latency_ms=min_lat,
            max_latency_ms=max_lat,
            mean_latency_ms=mean_lat,
        )
