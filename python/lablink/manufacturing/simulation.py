"""
High-Volume Seed-Controlled Manufacturing Simulation Engine.

Simulates automated manufacturing test runs for 100+ to 500+ DUTs with deterministic passing, out-of-limit, timeout, and communication failure rates.
"""

import random
from typing import Any

from lablink.manufacturing.dut import DUT, DUTStatus
from lablink.manufacturing.executor import ManufacturingExecutionResult, TestExecutor
from lablink.manufacturing.limits import ComparisonType, MeasurementLimit
from lablink.manufacturing.sequence import TestSequence, TestStep


class ManufacturingSimulationEngine:
    def __init__(
        self,
        seed: int = 42,
        station_id: str = "Station-Optical-01",
        sequence_version: str = "1.2",
    ) -> None:
        self.seed = seed
        self.station_id = station_id
        self.sequence_version = sequence_version
        self.executor = TestExecutor(station_id=station_id, software_version="1.0.0")

    def build_optical_module_sequence(self) -> TestSequence:
        seq = TestSequence(name="Optical Module Production Test", version=self.sequence_version)

        # Step 1: Instrument Connectivity Check
        def step_instrument_connectivity(dut: DUT, ctx: dict[str, Any]) -> list[dict[str, Any]]:
            fail_type = ctx.get("fail_type")
            if fail_type == "connection":
                raise ConnectionError("Optical Power Meter connection refused at 127.0.0.1:5025")
            return [{"name": "opm_status", "value": "CONNECTED", "source": "OPM_Simulator"}]

        seq.add_step(
            TestStep(
                name="Instrument Connectivity",
                action=step_instrument_connectivity,
                limits=[
                    MeasurementLimit(
                        measurement_name="opm_status",
                        unit="status",
                        expected_value="CONNECTED",
                        comparison_type=ComparisonType.EQUAL,
                    )
                ],
            )
        )

        # Step 2: Optical Power Measurement
        def step_optical_power(dut: DUT, ctx: dict[str, Any]) -> list[dict[str, Any]]:
            fail_type = ctx.get("fail_type")
            power = -3.2
            if fail_type == "optical_power_low":
                power = -8.5  # Below lower limit -5.0
            elif fail_type == "optical_power_high":
                power = 0.5  # Above upper limit -1.0
            return [{"name": "optical_power_dbm", "value": power, "source": "OPM_Simulator"}]

        seq.add_step(
            TestStep(
                name="Optical Power Measurement",
                action=step_optical_power,
                limits=[
                    MeasurementLimit(
                        measurement_name="optical_power_dbm",
                        unit="dBm",
                        lower_limit=-5.0,
                        upper_limit=-1.0,
                        comparison_type=ComparisonType.RANGE,
                    )
                ],
            )
        )

        # Step 3: Optical Oscilloscope Eye Rise Time
        def step_oscilloscope(dut: DUT, ctx: dict[str, Any]) -> list[dict[str, Any]]:
            fail_type = ctx.get("fail_type")
            rise_time = 25.4  # ps
            if fail_type == "rise_time_high":
                rise_time = 45.0  # Above upper limit 35.0 ps
            return [{"name": "rise_time_ps", "value": rise_time, "source": "Scope_Simulator"}]

        seq.add_step(
            TestStep(
                name="Optical Oscilloscope Measurement",
                action=step_oscilloscope,
                limits=[
                    MeasurementLimit(
                        measurement_name="rise_time_ps",
                        unit="ps",
                        lower_limit=10.0,
                        upper_limit=35.0,
                        comparison_type=ComparisonType.RANGE,
                    )
                ],
            )
        )

        # Step 4: Network Switch VLAN Validation
        def step_network_vlan(dut: DUT, ctx: dict[str, Any]) -> list[dict[str, Any]]:
            fail_type = ctx.get("fail_type")
            vlan_id = 100
            if fail_type == "vlan_mismatch":
                vlan_id = 999  # Mismatch
            return [{"name": "vlan_id", "value": vlan_id, "source": "Switch_Simulator"}]

        seq.add_step(
            TestStep(
                name="VLAN Tag Validation",
                action=step_network_vlan,
                limits=[
                    MeasurementLimit(
                        measurement_name="vlan_id",
                        unit="vlan",
                        expected_value=100,
                        comparison_type=ComparisonType.EQUAL,
                    )
                ],
            )
        )

        # Step 5: Ethernet Traffic Validation
        def step_traffic_validation(dut: DUT, ctx: dict[str, Any]) -> list[dict[str, Any]]:
            fail_type = ctx.get("fail_type")
            packet_loss = 0.0  # %
            if fail_type == "packet_loss":
                packet_loss = 4.5  # Above upper limit 1.0%
            return [{"name": "packet_loss_pct", "value": packet_loss, "source": "L2_Traffic_Sink"}]

        seq.add_step(
            TestStep(
                name="Ethernet Traffic Validation",
                action=step_traffic_validation,
                limits=[
                    MeasurementLimit(
                        measurement_name="packet_loss_pct",
                        unit="%",
                        upper_limit=1.0,
                        comparison_type=ComparisonType.LESS_THAN_EQUAL,
                    )
                ],
            )
        )

        return seq

    def run_simulation(
        self,
        num_duts: int = 100,
        fail_rate: float = 0.15,
        retest_failed: bool = True,
    ) -> list[ManufacturingExecutionResult]:
        rng = random.Random(self.seed)
        sequence = self.build_optical_module_sequence()
        all_execution_results: list[ManufacturingExecutionResult] = []

        fail_types_pool = [
            "optical_power_low",
            "optical_power_high",
            "rise_time_high",
            "vlan_mismatch",
            "packet_loss",
            "connection",
        ]

        for i in range(1, num_duts + 1):
            serial = f"SN-OPT-MODULE-{i:04d}"
            dut = DUT(
                serial_number=serial,
                part_number="PN-OPT-100G-LR4",
                hardware_revision="RevB",
                firmware_version="v2.1.0",
                status=DUTStatus.UNTESTED,
            )

            # Determine if first attempt fails
            will_fail = rng.random() < fail_rate
            context: dict[str, Any] = {}
            if will_fail:
                context["fail_type"] = rng.choice(fail_types_pool)

            # Run 1: First pass
            res1 = self.executor.execute_sequence(dut, sequence, context)
            all_execution_results.append(res1)

            # Optional Retest workflow if failed first attempt
            if will_fail and retest_failed:
                # 70% of failed DUTs pass on retest after reconfiguration/clean optical connector
                retest_will_pass = rng.random() < 0.70
                retest_context: dict[str, Any] = {}
                if not retest_will_pass:
                    retest_context["fail_type"] = context["fail_type"]

                res2 = self.executor.execute_sequence(dut, sequence, retest_context)
                all_execution_results.append(res2)

        return all_execution_results
