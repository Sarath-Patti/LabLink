# LabLink — Optical Test Automation

LabLink is an end-to-end optical instrument, Layer-1/Layer-2 network validation, and manufacturing test execution platform. It provides Python-driven test automation for optical devices, SCPI/VISA instrument control, and software Ethernet traffic generation alongside a C#/.NET 8 ASP.NET Core orchestration API, PostgreSQL data persistence, yield analytics, Docker containerization, and a declarative Jenkins CI/CD pipeline.

---

## Why LabLink?

Automating optical hardware and network testing requires coordinating physical transport interfaces, instrument protocols, test sequence execution, and persistent measurement telemetry. LabLink solves this by providing a unified, software-simulated test bench that decouples instrument drivers from physical hardware, enforces configurable measurement limits, classifies failures deterministically, and tracks unit-level manufacturing yield in a fully reproducible environment.

---

## Key Capabilities

* **Optical Instrument Automation:** Driver abstractions and software TCP/IP simulators for Optical Power Meters, Optical Switches, and Optical Oscilloscopes.
* **SCPI & VISA Abstractions:** IEEE 488.2 SCPI parser with VISA-style resource management over TCP/IP, Serial RS-232, and Mock transports.
* **Layer-1 / Layer-2 Network Validation:** Software MAC address formatting, 802.1Q VLAN tagging, Ethernet frame construction, and throughput/packet-loss traffic generation.
* **Manufacturing Test Engine:** Versioned test sequences with ordered execution steps, configurable measurement limits, timeouts, and bounded retries.
* **Deterministic Verdict Evaluation:** Automatic evaluation of range, boundary, and exact string limits returning `PASS`, `FAIL`, `ERROR`, or `SKIPPED` verdicts.
* **Machine-Readable Failure Classification:** Standardized failure codes (`INSTRUMENT_CONNECTION`, `MEASUREMENT_OUT_OF_LIMIT`, `PACKET_LOSS`, `TEST_TIMEOUT`, etc.).
* **DUT Measurement Traceability:** End-to-end unit tracking across serial numbers, part numbers, hardware revisions, firmware versions, and test runs.
* **Yield Analytics Engine:** Automatic calculation of First Pass Yield (FPY) vs. final yield after retest with failure breakdowns by step, station, and sequence version.
* **Service API & Persistence:** C# / .NET 8 ASP.NET Core REST API backed by PostgreSQL 15 and Entity Framework Core 8.0.
* **High-Volume Hardware Simulation:** Seed-controlled simulation engine testing 100+ to 500+ DUTs deterministically without physical hardware dependencies.
* **Containerized CI/CD:** Multi-stage Docker image, Docker Compose multi-service stack (`postgres` + `lablink-api`), Jenkins pipeline, and POSIX shell quality gates.

---

## System Architecture

```
                    LabLink Test Automation
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        Optical Tests     L1/L2 Tests     Simulation
              │               │               │
              └───────────────┼───────────────┘
                              ▼
                     Test Sequence Engine
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
          Measurements     Limits        Verdicts
                │             │             │
                └─────────────┼─────────────┘
                              ▼
                       C# / .NET API
                              │
                              ▼
                         PostgreSQL
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
           Test Reports              Yield Analytics
```

---

## Optical & Network Automation

LabLink provides modular driver abstractions and software TCP/IP simulators for core optical and network equipment:

* **Optical Power Meter (OPM):** Wavelength tuning (1310nm, 1550nm), optical power measurement (`dBm`, `mW`), auto-ranging, and zeroing calibration.
* **Optical Switch:** Channel selection, multi-port optical routing, and matrix status polling.
* **Optical Oscilloscope:** Signal acquisition, waveform sampling, peak-to-peak amplitude calculation, and eye diagram rise-time measurement.
* **Network Switch:** Port state configuration, link status polling, and VLAN mapping.
* **Protocols & Transports:** IEEE 488.2 SCPI command formatting (`*IDN?`, `*RST`, `*CLS`, `SYST:ERR?`) over TCP/IP, Serial RS-232, and Mock transports via a VISA-style resource manager.

*Note: Instrument drivers interface with software TCP/IP SCPI simulators running on `127.0.0.1`, enabling complete hardware-independent automated testing without requiring physical optical equipment.*

---

## Manufacturing Test Engine

The manufacturing engine structures production test execution into a deterministic pipeline:

```
DUT -> Versioned Test Sequence -> Ordered Test Steps -> Instrument Measurements -> Limits -> Verdict -> Persistent Result
```

* **Versioned Test Sequences (`TestSequence`):** Groups ordered test steps (e.g., "Optical Module Production Test v1.2").
* **Execution & Retry Policies (`TestExecutor`):** Configurable per-step timeouts and bounded retries to handle transient communication faults.
* **Limit Evaluation (`LimitEvaluator`):** Evaluates numeric or string measurements against `RANGE`, `LESS_THAN_EQUAL`, `GREATER_THAN_EQUAL`, or `EQUAL` criteria.
* **Verdict Assignment (`VerdictEngine`):** Computes step and overall DUT verdicts (`PASS`, `FAIL`, `ERROR`, `SKIPPED`).
* **Failure Classification (`FailureCode`):** Maps errors to machine-readable codes for automated yield analysis.

---

## Test Data & Yield Analytics

LabLink provides persistent traceability and quality metrics across manufacturing runs:

* **Unit Traceability:** Every test run is linked to a unique `DUT` serial number, part number, hardware revision, firmware version, test station ID, and sequence version.
* **First Pass Yield (FPY):** Calculated strictly from first-pass test attempts, distinguished from final yield after retest attempts.
* **Failure Breakdown:** Aggregates failures by test step, machine failure code, station ID, and sequence version.
* **Reporting:** Relational persistence in PostgreSQL via EF Core with JSON and CSV report export utilities (`ManufacturingReporter`).

---

## Manufacturing Simulation Results

The seed-controlled simulation engine (`ManufacturingSimulationEngine`) evaluates high-volume production sweeps:

| Metric | Result |
|---|---:|
| DUTs Tested | 100 |
| Total Test Runs | 113 |
| First Pass Yield (FPY) | 87.0% |
| Final Yield (w/ Retest) | 94.0% |

*Note: The simulation is seed-controlled (`seed=42`) and fully deterministic. Execution timing (`0.03 ms/run`) measures software simulation pipeline throughput rather than physical optical hardware settling latency.*

---

## API & Persistence

The service layer provides centralized orchestration and persistence:

* **C# / .NET 8 Web API (`LabLink.Api`):** REST API built with ASP.NET Core, feature controllers (`DutsController`, `ManufacturingController`, `TestCasesController`, `TestRunsController`, `TestResultsController`, `DevicesController`, `InstrumentsController`), and exception handling middleware.
* **PostgreSQL Persistence (`LabLinkDbContext`):** Relational schema managed via EF Core 8.0 migrations (`InitialPostgresSchema`, `AddManufacturingModels`).
* **OpenAPI Documentation:** Interactive Swagger UI available at `/swagger`.
* **In-Memory Fallback:** Thread-safe in-memory repositories for isolated testing environments.

---

## Testing & Quality

LabLink maintains automated quality gates across Python and .NET:

### Python
* **Ruff:** 0 lint errors
* **Black:** 100% code formatted
* **Mypy:** 0 type errors
* **Pytest:** 141 / 141 tests passing

### .NET
* **Build:** 0 compilation errors, 0 warnings
* **xUnit Tests:** 16 / 16 tests passing
* **Format Verification:** 0 formatting diffs

### Validation
* **Docker Smoke Test:** Passed cleanly against containerized stack
* **Master CI Pipeline:** 8 / 8 stages passed
* **100-DUT Manufacturing Simulation:** Passed cleanly with deterministic yield metrics

Test categories include **Unit**, **Functional**, **Integration** (TCP sockets & REST API), **Regression**, **Negative** (timeouts, malformed inputs), and **Performance** (latency & high-volume simulation benchmarks).

---

## CI/CD & Reproducibility

The complete quality pipeline is fully reproducible locally and in CI:

* **Jenkins Pipeline:** Declarative `Jenkinsfile` executing 11 automated stages.
* **POSIX Shell Scripts:** Modular scripts in `scripts/` automating environment setup, static checks, unit tests, PostgreSQL startup, EF Core migrations, API smoke tests, and cleanup.
* **Docker Orchestration:** Multi-stage Dockerfile producing a lightweight runtime image and Docker Compose (`postgres:15-alpine` + `lablink-api:0.9.0`) with native health checks (`pg_isready`, `/api/v1/health`).

Primary CI execution command:
```bash
./scripts/ci.sh
```

---

## Technology Stack

| Area | Technologies |
|---|---|
| Automation Framework | Python 3.11, Pytest |
| Instrument Protocols | SCPI, VISA-style resource manager |
| Physical Transports | TCP/IP, Serial RS-232, Mock |
| Networking Validation | Layer 1 / Layer 2 Ethernet, MAC, 802.1Q VLAN, Traffic Generator/Sink |
| Backend Service | C#, .NET 8 ASP.NET Core, OpenAPI/Swagger |
| Database & ORM | PostgreSQL 15, Entity Framework Core 8.0 |
| CI/CD Pipeline | Jenkins Declarative Pipeline, POSIX Shell |
| Containerization | Docker, Docker Compose |
| Quality Gates | Ruff, Black, Mypy, xUnit |

---

## Quick Start

### 1. Run Python Test Suite
```bash
cd python
source .venv/bin/activate
pytest -v
```

### 2. Run .NET API Service
```bash
dotnet run --project dotnet/LabLink.Api/LabLink.Api.csproj
```

### 3. Run Containerized Full-Stack Environment
```bash
docker compose -f docker/docker-compose.yml up --build
```

### 4. Run Master Local CI Pipeline
```bash
./scripts/ci.sh
```

### 5. Run Manufacturing Simulation Demo
```bash
.venv/bin/python -m lablink.manufacturing.run_demo --duts 100 --seed 42
```

---

## Project Structure

```
LabLink/
├── Jenkinsfile              # Declarative Jenkins CI/CD pipeline
├── docker/
│   └── docker-compose.yml   # Multi-service Docker Compose orchestration
├── dotnet/
│   ├── LabLink.Api/         # ASP.NET Core Web API & EF Core persistence
│   └── LabLink.Api.Tests/   # xUnit WebApplicationFactory test suite
├── python/
│   ├── lablink/
│   │   ├── instruments/     # Optical instrument drivers (OPM, Switch, Scope)
│   │   ├── transport/       # BaseTransport, TCP, Serial RS-232, Mock
│   │   ├── protocols/       # SCPI protocol & VISA resource management
│   │   ├── network/         # L2 Ethernet, MAC, 802.1Q VLAN, Traffic engine
│   │   ├── manufacturing/   # DUT, sequence, limits, verdict, yield analytics
│   │   └── integration/     # LabLinkAPIClient HTTP integration client
│   └── tests/
│       ├── unit/            # Component unit tests
│       ├── functional/      # Instrument & L2 functional tests
│       ├── integration/     # TCP socket & REST API integration tests
│       ├── regression/      # End-to-end regression suite
│       ├── negative/        # Negative & error handling tests
│       └── performance/     # Latency & simulation benchmarks
├── scripts/                 # Modular CI/CD & Docker shell scripts
└── docs/                    # Architectural documentation
```

---

## Engineering Highlights

* **Hardware-Independent Instrument Automation:** Decoupled SCPI and transport architecture allowing total software simulation without physical optical hardware.
* **Versioned Manufacturing Test Sequences:** Structured execution of ordered test steps with configurable limits, timeouts, and bounded retries.
* **Deterministic Verdict Engine:** Automated PASS/FAIL/ERROR verdict evaluation with machine-readable failure classification.
* **Traceable Test Persistence:** DUT-level measurement traceability backed by a C#/.NET 8 API and PostgreSQL database.
* **Integrated L1/L2 Network Validation:** Software Ethernet frame generation, VLAN tagging, and packet loss/throughput measurement alongside optical testing.
* **High-Volume Deterministic Simulation:** Seed-controlled 100+ DUT manufacturing simulation generating realistic First Pass Yield (FPY) and retest metrics.
* **Reproducible CI/CD Environment:** Single-command local CI reproduction (`./scripts/ci.sh`) matching containerized Jenkins and Docker Compose deployment.

---

## Development History

| Version | Focus Area |
|---|---|
| v0.1 | Foundation & Core Package Structure |
| v0.2 | Transport & SCPI Protocol Layer |
| v0.3 | Optical Instruments & TCP Simulators |
| v0.4 | Pytest Test Automation Framework |
| v0.5 | Layer-1 / Layer-2 Ethernet & Network Validation |
| v0.6 | C# / .NET 8 REST Orchestration API |
| v0.7 | PostgreSQL Persistence & EF Core Migrations |
| v0.8 | Jenkins & POSIX Shell CI/CD Quality Pipeline |
| v0.9 | Containerized Multi-Service Docker Deployment |
| v1.0 | Manufacturing Test Execution, Measurement Traceability & Yield Analytics |
