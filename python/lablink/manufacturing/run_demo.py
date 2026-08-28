"""
Reproducible CLI Demonstration Entry Point.

Executes a high-volume seed-controlled manufacturing simulation, logs progress, posts runs to the API (if running), and prints yield analytics & reports.

Usage:
    python -m lablink.manufacturing.run_demo --duts 100 --seed 42
"""

import argparse
import json
import time

from lablink.integration.api_client import LabLinkAPIClient
from lablink.manufacturing.analytics import YieldAnalytics, YieldMetrics
from lablink.manufacturing.executor import ManufacturingExecutionResult
from lablink.manufacturing.reporting import ManufacturingReporter
from lablink.manufacturing.simulation import ManufacturingSimulationEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="LabLink v1.0 Manufacturing Demonstration Engine")
    parser.add_argument("--duts", type=int, default=100, help="Number of simulated DUTs to test")
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for deterministic simulation"
    )
    parser.add_argument(
        "--api-url", type=str, default="http://localhost:5099", help="Target API URL"
    )
    args = parser.parse_args()

    print("=========================================================================")
    print("   LABLINK v1.0 MANUFACTURING TEST EXECUTION & YIELD ANALYTICS DEMO     ")
    print("=========================================================================")
    print(f"Target DUT Count : {args.duts}")
    print(f"Random Seed      : {args.seed}")
    print(f"API Target URL   : {args.api_url}")
    print()

    start_time = time.perf_counter()

    engine = ManufacturingSimulationEngine(seed=args.seed)
    results: list[ManufacturingExecutionResult] = engine.run_simulation(
        num_duts=args.duts, fail_rate=0.15
    )

    end_time = time.perf_counter()
    total_duration_sec = round(end_time - start_time, 3)
    avg_duration_ms = round((total_duration_sec / len(results)) * 1000.0, 2) if results else 0.0

    metrics: YieldMetrics = YieldAnalytics.calculate_yield(results)

    # Attempt to post simulation telemetry to API if online
    try:
        client = LabLinkAPIClient(args.api_url)
        health = client.health_check()
        if health.get("status") == "Healthy":
            print(f"[+] API Service Connected at {args.api_url} (Version: {health.get('version')})")
            print("[+] Syncing manufacturing run telemetry with PostgreSQL database...")
            for r in results[:10]:
                try:
                    client.create_dut(
                        r.dut_serial,
                        part_number="PN-OPT-100G",
                        hardware_revision="RevB",
                        firmware_version="v2.1.0",
                    )
                except RuntimeError:
                    pass
                try:
                    run = client.create_manufacturing_run(
                        r.dut_serial,
                        station_id=r.station_id,
                        sequence_name=r.sequence_name,
                        sequence_version=r.sequence_version,
                    )
                    run_id = run["id"]
                    for m in r.all_measurements:
                        client.add_measurement(
                            run_id=run_id,
                            step_name=m.step_name,
                            measurement_name=m.measurement_name,
                            value=m.value,
                            unit=m.unit,
                            lower_limit=m.lower_limit,
                            upper_limit=m.upper_limit,
                            expected_value=str(m.expected_value) if m.expected_value else None,
                            verdict=m.verdict.value,
                            failure_code=m.failure_code.value,
                            instrument_source=m.instrument_source,
                        )
                    client.complete_manufacturing_run(
                        run_id,
                        verdict=r.overall_verdict.value,
                        failure_code=r.failure_code.value,
                        failure_summary=r.failure_summary,
                    )
                except RuntimeError as ex:
                    print(f"[-] API sync note for {r.dut_serial}: {ex}")
    except RuntimeError:
        print("[!] API service offline; simulation results computed in-memory.")

    print()
    print("=========================================================================")
    print("                 MANUFACTURING YIELD ANALYTICS SUMMARY                   ")
    print("=========================================================================")
    print(f"Total DUTs Tested            : {metrics.total_units_tested}")
    print(f"Total Test Runs Executed     : {len(results)}")
    print(f"First-Pass Passed DUTs       : {metrics.first_pass_passed}")
    print(f"FIRST PASS YIELD (FPY)       : {metrics.first_pass_yield_percentage}%")
    print(f"Final Passed DUTs (w/ Retest): {metrics.final_passed}")
    print(f"FINAL YIELD                  : {metrics.final_yield_percentage}%")
    print(f"Total Simulation Pipeline Run: {total_duration_sec}s")
    print(f"Average Execution Time/Run   : {avg_duration_ms}ms")
    print()
    print("--- Failure Breakdown by Test Step ---")
    for step_name, count in metrics.failures_by_step.items():
        print(f"  * {step_name:<35} : {count} failure(s)")

    print()
    print("--- Failure Breakdown by Machine Code ---")
    for code, count in metrics.failures_by_code.items():
        print(f"  * {code:<35} : {count} occurrence(s)")

    print()
    summary_report = ManufacturingReporter.generate_summary_report(results)
    print("=========================================================================")
    print("               JSON MANUFACTURING REPORT EXPORT (SAMPLE)                 ")
    print("=========================================================================")
    print(json.dumps(summary_report, indent=2))
    print("=========================================================================")


if __name__ == "__main__":
    main()
