"""
Regression Test Suite — End-to-End Automated Optical & Layer-2 Network Test Bench Workflow.

Executes complete multi-instrument and Layer-2 network validation test bench scenarios
to verify end-to-end system regression stability across Python drivers, protocols, and network models.
"""

import pytest

from lablink.devices.network_switch import NetworkSwitch
from lablink.instruments.optical_power_meter import OpticalPowerMeter
from lablink.instruments.optical_switch import OpticalSwitch
from lablink.network.traffic import TrafficGenerator, TrafficSink
from tests.utilities.assertions import assert_within_tolerance
from tests.utilities.reporting import JSONResultExporter, TestMeasurementResult


@pytest.mark.regression
def test_automated_optical_test_bench_regression(
    opm_client: OpticalPowerMeter, switch_client: OpticalSwitch
) -> None:
    """
    Verify complete multi-instrument optical test bench regression workflow:
    1. Identify all test instruments.
    2. Route optical matrix to target channel.
    3. Tune power meter wavelength.
    4. Measure optical power level.
    5. Verify zero SCPI errors across all instruments.
    """
    exporter = JSONResultExporter("test_results.json")

    # Step 1: Verify instrument identifications
    opm_idn = opm_client.identify()
    switch_idn = switch_client.identify()

    assert "N5767A-OPM" in opm_idn
    assert "MAP-200-SW" in switch_idn

    # Step 2: Test bench execution loop across multiple channels and wavelengths
    test_matrix = [
        (1, 1310.0, -10.0),
        (3, 1550.0, -10.0),
        (5, 1625.0, -10.0),
    ]

    for channel, wavelength, expected_power in test_matrix:
        switch_client.set_route(channel)
        assert switch_client.get_route() == channel

        opm_client.set_wavelength(wavelength)
        assert_within_tolerance(opm_client.get_wavelength(), wavelength, 0.01)

        measured_power = opm_client.measure_power()
        assert_within_tolerance(
            measured_power,
            expected_power,
            0.001,
            f"Power check failed at Ch{channel} @ {wavelength}nm",
        )

        exporter.record_result(
            TestMeasurementResult(
                test_name="automated_optical_test_bench_regression",
                category="regression",
                status="PASS",
                duration_ms=12.5,
                instrument="OpticalPowerMeter",
                measurement_name="optical_power",
                expected=expected_power,
                actual=measured_power,
                unit="dBm",
            )
        )

    # Step 3: Check system error queues to ensure clean execution
    opm_client.check_system_errors()
    switch_client.check_system_errors()

    # Step 4: Export telemetry
    report_path = exporter.export()
    assert report_path.is_file()


@pytest.mark.regression
@pytest.mark.l2
def test_multidomain_l2_network_and_optical_regression(
    opm_client: OpticalPowerMeter,
    net_switch_client: NetworkSwitch,
    traffic_generator: TrafficGenerator,
    traffic_sink: TrafficSink,
) -> None:
    """
    Verify multi-domain integrated optical & Layer-2 network test bench regression scenario:
    1. Verify NetworkSwitch control and enable target port.
    2. Route optical channel to OPM and measure power level.
    3. Transmit 802.1Q tagged Ethernet frame traffic stream.
    4. Analyze sink performance (zero packet loss, positive throughput).
    5. Verify clean execution with zero SCPI errors.
    """
    # 1. Device control
    assert net_switch_client.get_port_count() == 24
    net_switch_client.enable_port(1)
    assert net_switch_client.get_port_state(1) is True

    # 2. Optical measurement
    opm_client.set_wavelength(1550.0)
    assert opm_client.measure_power() == -10.0

    # 3. Traffic stream execution
    frames = traffic_generator.generate_frames()
    tx_bytes = sum(f.frame_size for f in frames)

    for frame in frames:
        traffic_sink.process_frame(frame)

    # 4. Traffic analysis
    stats = traffic_sink.analyze(
        transmitted_count=len(frames),
        transmitted_bytes=tx_bytes,
        duration_sec=0.05,
    )

    assert stats.transmitted_packets == 50
    assert stats.received_packets == 50
    assert stats.lost_packets == 0
    assert stats.packet_loss_percentage == 0.0
    assert stats.throughput_bytes_per_sec > 0.0

    # 5. Clean error status check
    opm_client.check_system_errors()
    net_switch_client.check_system_errors()
