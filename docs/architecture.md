# LabLink High-Level System Architecture

## Architecture Overview

LabLink is a multi-tier network, laboratory instrument, and manufacturing test automation platform designed with strict separation of concerns across technical stacks:

1. **Python Layer (`python/`)**
   * **Role:** Primary test automation engine, instrument integration, protocol parsing, hardware transport execution, Layer-2 Ethernet validation, software traffic generation, standard-library HTTP API client (`LabLinkAPIClient`), pytest automation framework, and the **v1.0 Manufacturing Engine** (`lablink.manufacturing`).
   * **Responsibility:** Executes SCPI commands, manages TCP/IP, RS-232 serial, and Layer-2 Ethernet streams, drives instrument drivers, software simulators, software traffic engines, executes versioned manufacturing test sequences (`TestSequence`), evaluates measurement limits (`LimitEvaluator`), calculates deterministic verdicts (`VerdictEngine`), classifies failure codes (`FailureCode`), calculates yield analytics (`YieldAnalytics`), generates manufacturing reports (`ManufacturingReporter`), and executes seed-controlled high-volume simulations (`ManufacturingSimulationEngine`).

2. **C#/.NET Layer (`dotnet/LabLink.Api` & `dotnet/LabLink.Api.Tests`)**
   * **Role:** Test management, orchestration, manufacturing persistence API, and external Web API platform.
   * **Responsibility:** Manages test case definitions, test run lifecycles, test result ingestion, device/instrument metadata, DUT records (`Dut`), manufacturing runs (`ManufacturingRun`), measurement records (`MeasurementRecord`), exposes REST endpoints (`/api/v1/`), provides OpenAPI/Swagger documentation, and maintains EF Core PostgreSQL database persistence.

3. **Persistence Layer (`dotnet/LabLink.Api/Persistence`)**
   * **Role:** Relational database storage and schema migration.
   * **Responsibility:** `LabLinkDbContext` with EF Core 8.0 mapping `TestCase`, `TestRun`, `TestResult`, `Device`, `Instrument`, `Dut`, `ManufacturingRun`, and `MeasurementRecord` entities to PostgreSQL.

4. **CI/CD Pipeline (`Jenkinsfile` & `scripts/`)**
   * **Role:** Automated quality verification and pipeline orchestration.
   * **Responsibility:** Declarative Jenkins pipeline and POSIX-compliant modular shell scripts executing static analysis, testing, PostgreSQL service startup, database migration, API startup, manufacturing simulation, and end-to-end integration smoke testing.

5. **Containerized Deployment Layer (`docker/` & `dotnet/LabLink.Api/Dockerfile`)**
   * **Role:** Multi-service container orchestration and reproducible deployment.
   * **Responsibility:** Multi-stage Dockerfile packaging `LabLink.Api` into a lightweight runtime image; Docker Compose orchestrating `postgres` and `lablink-api` with native health checks (`pg_isready`, `/api/v1/health`) and named persistent volume storage (`lablink-postgres-data`).

```
                 DUT
                  │
                  ▼
          Manufacturing Run
                  │
                  ▼
          Versioned Sequence
                  │
          ┌───────┴────────┐
          ▼                ▼
   Optical Tests       L1/L2 Tests
          │                │
          └───────┬────────┘
                  ▼
             Measurements
                  │
                  ▼
             Verdict Engine
                  │
             ┌────┴────┐
             ▼         ▼
           PASS       FAIL
             │         │
             └────┬────┘
                  ▼
             .NET API
                  │
                  ▼
              PostgreSQL
                  │
          ┌───────┴────────┐
          ▼                ▼
     Test Reports     Yield Analytics
```

---

## Milestone v1.0 Manufacturing System Architecture

### 1. DUT Traceability Model
`DUT` domain model and `Dut` EF Core entity track units under test by unique serial number, part number, hardware revision, firmware version, and status (`Untested`, `Passed`, `Failed`, `Scrapped`).

### 2. Versioned Test Sequences & Step Execution
`TestSequence` encapsulates ordered `TestStep` instances with configurable measurement limits (`MeasurementLimit`), timeouts, retry policies, and fail-fast options.

### 3. Verdict Engine & Failure Classification
`VerdictEngine` enforces deterministic verdict calculation (`PASS`, `FAIL`, `ERROR`, `SKIPPED`) and maps failures to machine-readable codes (`FailureCode`: `NONE`, `INSTRUMENT_CONNECTION`, `INSTRUMENT_TIMEOUT`, `MEASUREMENT_OUT_OF_LIMIT`, `NETWORK_CONNECTIVITY`, `VLAN_CONFIGURATION`, `PACKET_LOSS`, `TRAFFIC_FAILURE`, `TEST_TIMEOUT`, `CONFIGURATION_ERROR`, `SOFTWARE_ERROR`).

### 4. Yield Analytics & Reporting Engine
`YieldAnalytics` calculates First Pass Yield (FPY) and final yield after retest. `ManufacturingReporter` exports structured JSON, CSV, and summary reports from persisted data.

---

## Implementation Status (Milestones v0.1 – v1.0)

### Implemented Functionality
* [x] Abstract transport interface contract (`BaseTransport`) & client transports (`TCPTransport`, `SerialTransport`, `MockTransport`)
* [x] SCPI protocol handler (`SCPIProtocol`) & IEEE 488.2 common commands (`*IDN?`, `*RST`, `*CLS`, `SYST:ERR?`)
* [x] VISA-style resource manager (`VISAResourceManager`) & resource wrapper (`VISAResource`)
* [x] Base instrument abstraction (`BaseInstrument`) & concrete instrument drivers (`OpticalPowerMeter`, `OpticalSwitch`, `OpticalOscilloscope`, `NetworkSwitch`)
* [x] In-process TCP SCPI software simulators (`OpticalPowerMeterSimulator`, `OpticalSwitchSimulator`, `OpticalOscilloscopeSimulator`, `NetworkSwitchSimulator`)
* [x] Layer-2 MAC address value object (`MACAddress`) & 802.1Q VLAN tag model (`VLANHeader`)
* [x] Ethernet MAC frame modeling (`EthernetFrame`) & telemetry header embedding
* [x] Software traffic generator (`TrafficGenerator`), receiver/sink (`TrafficSink`), and statistics engine (`TrafficStatistics`)
* [x] Pytest test automation framework structure & markers (`l2`, `functional`, `regression`, `negative`, `performance`, `instrument`, `simulator`, `integration`, `manufacturing`)
* [x] C# ASP.NET Core Web API orchestration layer (`Controllers`, `Services`, `Domain`, `Repositories`, `Middleware`)
* [x] PostgreSQL database persistence (`LabLinkDbContext`) & EF Core migrations (`InitialPostgresSchema`, `AddManufacturingModels`)
* [x] Declarative Jenkins CI/CD pipeline (`Jenkinsfile`) & POSIX-compliant shell scripts (`scripts/*.sh`)
* [x] Multi-Stage Dockerfile & Multi-Service Docker Compose Stack (`docker/docker-compose.yml`)
* [x] DUT model (`DUT`), versioned test sequence (`TestSequence`), test step executor (`TestExecutor`), limit evaluator (`LimitEvaluator`), verdict engine (`VerdictEngine`), machine-readable failure classification (`FailureCode`)
* [x] Yield analytics engine (`YieldAnalytics`), reporting exporter (`ManufacturingReporter`), CLI entry point (`run_demo.py`), seed-controlled simulation engine (`ManufacturingSimulationEngine`)
* [x] C# REST API manufacturing endpoints (`DutsController`, `ManufacturingController`), DTOs, EF Core entity mappings, and xUnit integration tests

### Deliberately Deferred Functionality (Future Roadmap)
* [ ] Physical optical equipment validation (No physical optical hardware attached)
* [ ] NI-VISA native binary driver bindings — *Deferred*
* [ ] IXIA hardware integration — *Deferred*
* [ ] Kernel-bypass networking / DPDK drivers — *Deferred*
* [ ] Kubernetes / ArgoCD deployment — *Deferred*
