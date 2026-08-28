# LabLink: Manufacturing Test Execution, Measurement Traceability & Yield Analytics Platform

LabLink is an extensible, multi-tier network, laboratory instrument, and manufacturing test automation platform. It provides Python-based instrument control, networking transport abstractions, software Layer-2 Ethernet validation, and versioned manufacturing test execution alongside a C#/.NET 8 ASP.NET Core service layer for test management, run orchestration, PostgreSQL data persistence, yield analytics, declarative Jenkins CI/CD automation, and multi-service Docker/Docker Compose containerization.

---

## Architecture Overview

LabLink employs a decoupled multi-tiered architecture:

* **Python Layer (`python/`):** Primary engine for test automation, physical/network transport handling (TCP/IP, Serial RS-232, Mock), SCPI protocol parsing, VISA-style resource management, instrument abstractions, optical equipment simulators, Layer-2 Ethernet frame modeling, 802.1Q VLAN tagging, software traffic generation/analysis, standard-library HTTP integration client (`LabLinkAPIClient`), pytest automation framework, and the **v1.0 Manufacturing Engine** (`lablink.manufacturing`) providing DUT models, versioned test sequences, test step execution, limit evaluation, deterministic verdict calculation, failure classification, yield analytics, and high-volume seed-controlled simulation.
* **C# / .NET Layer (`dotnet/LabLink.Api` & `dotnet/LabLink.Api.Tests`):** Service layer providing an ASP.NET Core Web API orchestration foundation, domain models (`TestCase`, `TestRun`, `TestResult`, `Device`, `Instrument`, `Dut`, `ManufacturingRun`, `MeasurementRecord`), DTOs, application services, thin REST controllers (`TestCasesController`, `TestRunsController`, `TestResultsController`, `DevicesController`, `InstrumentsController`, `DutsController`, `ManufacturingController`), exception middleware, OpenAPI/Swagger documentation, and xUnit test suite.
* **Persistence Layer (`dotnet/LabLink.Api/Persistence`):** PostgreSQL Entity Framework Core 8.0 relational database persistence (`LabLinkDbContext`) supporting test run history, test results telemetry, DUT records, manufacturing runs, measurement records, EF Core migrations (`InitialPostgresSchema`, `AddManufacturingModels`), and fallback thread-safe in-memory repositories.
* **CI/CD Pipeline (`Jenkinsfile` & `scripts/`):** Reproducible declarative Jenkins CI/CD pipeline and POSIX-compliant modular shell scripts automating static quality checks, unit/functional testing, Docker PostgreSQL service management, EF Core migrations, background API startup, high-volume manufacturing simulation, and end-to-end HTTP smoke integration tests.
* **Containerized Deployment Layer (`docker/` & `dotnet/LabLink.Api/Dockerfile`):** Multi-stage Docker build producing lightweight ASP.NET 8.0 runtime images and Docker Compose multi-service orchestration (`postgres` + `lablink-api`) with native health checks (`pg_isready`, `/api/v1/health`) and named persistent volume data storage (`lablink-postgres-data`).

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

## Technology Stack

* **Automation & Manufacturing Engine:** Python 3.11 (`lablink.manufacturing`)
* **Test Framework:** pytest (with markers, fixtures, custom assertions, JUnit XML output, and JSON telemetry export)
* **Networking & Layer-2 Validation:** Software EthernetFrame, MACAddress, 802.1Q VLANHeader, TrafficGenerator, TrafficSink, TrafficStatistics
* **Service API:** C# / .NET 8.0 ASP.NET Core Web API with OpenAPI/Swagger
* **API Test Framework:** xUnit, Microsoft.AspNetCore.Mvc.Testing WebApplicationFactory
* **ORM & Database:** Entity Framework Core 8.0, PostgreSQL 15 (`Npgsql.EntityFrameworkCore.PostgreSQL`)
* **Containers & Orchestration:** Multi-stage Dockerfile, Docker Compose (`docker/docker-compose.yml`), PostgreSQL Alpine container, persistent named volume
* **CI/CD & Shell Automation:** Jenkins Declarative Pipeline (`Jenkinsfile`), POSIX Bash (`scripts/`)

---

## Milestone v1.0 Manufacturing Test Execution Architecture

### 1. DUT Model (`DUT` & `Dut` EF Core Entity)
Traces unit under test history via unique serial number, part number, hardware revision, firmware version, creation timestamp, and overall status (`Untested`, `Passed`, `Failed`, `Scrapped`).

### 2. Versioned Test Sequences (`TestSequence` & `TestStep`)
Defines ordered manufacturing test sequences (e.g. "Optical Module Production Test v1.2") containing test steps with configurable limits, timeouts, retry policies, and critical flags.

### 3. Configurable Limits & Evaluator (`MeasurementLimit` & `LimitEvaluator`)
Evaluates numeric or string measurements against lower, upper, range, or exact expected values (`RANGE`, `LESS_THAN_EQUAL`, `GREATER_THAN_EQUAL`, `EQUAL`).

### 4. Deterministic Verdict Engine & Failure Codes (`VerdictEngine` & `FailureCode`)
Calculates step and overall DUT verdicts (`PASS`, `FAIL`, `ERROR`, `SKIPPED`) and maps failures to machine-readable failure codes (`NONE`, `INSTRUMENT_CONNECTION`, `INSTRUMENT_TIMEOUT`, `MEASUREMENT_OUT_OF_LIMIT`, `NETWORK_CONNECTIVITY`, `VLAN_CONFIGURATION`, `PACKET_LOSS`, `TRAFFIC_FAILURE`, `TEST_TIMEOUT`, `CONFIGURATION_ERROR`, `SOFTWARE_ERROR`).

### 5. Yield Analytics & Retest Differentiation (`YieldAnalytics`)
Calculates First Pass Yield (FPY) based strictly on first test attempts, distinguishes FPY from final yield after retest, and provides failure breakdowns by step, machine code, station ID, and sequence version.

### 6. High-Volume Seed-Controlled Simulation (`ManufacturingSimulationEngine`)
Executes seed-controlled simulation sweeps for 100+ to 500+ DUTs with deterministic passing, out-of-limit, timeout, and connection failure rates using software simulators without physical hardware.

---

## Measured Performance Benchmarks

* **Simulation Size:** 100 Simulated DUTs (113 Total Executed Runs)
* **Random Seed:** `42`
* **First Pass Yield (FPY):** `87.0%` (87/100 Passed First Attempt)
* **Final Yield (w/ Retest):** `94.0%` (94/100 Passed Final Attempt)
* **Total Simulation Pipeline Time:** `0.003 seconds`
* **Average Execution Time/Run:** `0.03 ms/run`
* *Note: Benchmarks measure software simulation pipeline execution throughput without physical hardware latency.*

---

## Repository Structure

```
LabLink/
├── Jenkinsfile              # Declarative Jenkins CI/CD pipeline definition
├── .dockerignore            # Docker image build ignore rules
├── .env.example             # Safe environment variable configuration template
├── python/
│   ├── lablink/
│   │   ├── config/          # Environment-aware settings & config management
│   │   ├── logging/         # Credential-redacting logging framework
│   │   ├── transport/       # BaseTransport, TCPTransport, SerialTransport, MockTransport
│   │   ├── protocols/       # SCPIProtocol, VISAResource, VISAResourceManager
│   │   ├── instruments/     # BaseInstrument, OpticalPowerMeter, OpticalSwitch, OpticalOscilloscope
│   │   ├── devices/         # NetworkSwitch device control abstraction
│   │   ├── simulators/      # BaseInstrumentSimulator, OpticalPowerMeterSimulator, OpticalSwitchSimulator, OpticalOscilloscopeSimulator, NetworkSwitchSimulator
│   │   ├── network/         # MACAddress, VLANHeader, EthernetFrame, TrafficGenerator, TrafficSink, TrafficStatistics
│   │   ├── manufacturing/   # DUT, MeasurementLimit, VerdictEngine, TestSequence, TestExecutor, YieldAnalytics, ManufacturingReporter, ManufacturingSimulationEngine, run_demo
│   │   └── integration/     # LabLinkAPIClient Python ↔ C# REST API integration client
│   └── tests/
│       ├── conftest.py      # Reusable fixtures (simulators, connected clients, L2 frames/traffic, config)
│       ├── unit/            # Unit tests for transports, SCPI, VISA, instruments, simulators, MAC, VLAN, Ethernet, traffic, DUT, limits, verdict, executor
│       ├── integration/     # TCP socket integration tests and Python ↔ C# REST API integration test
│       ├── functional/      # Functional tests for OPM, Switch, Scope, Network Switch, L2 frames, manufacturing
│       ├── regression/      # End-to-end multi-instrument & L2 network automated test bench regression suite
│       ├── negative/        # Negative boundary, invalid input, malformed MAC/VLAN, and error handling tests
│       ├── performance/     # SCPI query latency, measurement throughput, L2 benchmarks, high-volume simulation benchmarks
│       └── utilities/       # Custom assertions, timing helpers, JSON result exporter
│
├── dotnet/
│   ├── LabLink.Api/         # ASP.NET Core Web API (Dockerfile, Controllers, Services, Domain, Repositories, Persistence, Migrations)
│   └── LabLink.Api.Tests/   # Automated xUnit WebApplicationFactory & PostgreSQL integration test suite
│
├── docker/
│   └── docker-compose.yml   # Multi-service Docker Compose orchestration (postgres + lablink-api)
│
├── scripts/                 # Modular CI/CD & Docker management shell scripts
│   ├── ci.sh                # Master local CI reproduction script
│   ├── docker_up.sh         # Docker Compose image build, stack startup & health polling
│   ├── docker_down.sh       # Docker Compose stack clean shutdown (preserves volume)
│   ├── docker_migrate.sh    # EF Core database migration against containerized PostgreSQL
│   ├── docker_smoke_test.sh # Containerized REST API & manufacturing smoke test
│   ├── setup_python.sh      # Python virtual environment setup
│   ├── run_python_quality.sh# Ruff, Black, and Mypy static quality checks
│   ├── run_python_tests.sh  # Pytest suite with JUnit XML generation
│   ├── run_dotnet_tests.sh  # .NET restore, build, format verify, and xUnit execution
│   ├── start_postgres.sh    # Docker PostgreSQL container startup
│   ├── wait_for_postgres.sh # PostgreSQL readiness polling
│   ├── migrate_database.sh  # EF Core database migration application
│   ├── start_api.sh         # Background API server startup and health polling
│   ├── run_integration_tests.sh # REST API smoke workflow execution
│   └── cleanup.sh           # API process termination and container cleanup
│
├── config/                  # Safe configuration templates (.json, .env)
├── docs/                    # Architectural & design documentation
├── ethernet/                # Layer-2 Ethernet test components
└── jenkins/                 # Jenkins CI/CD configuration files
```

---

## Milestone History

* [x] **v0.1 Foundation:** Core Python package structure, `.gitignore`, logging, pytest setup, C# ASP.NET Core Web API foundation.
* [x] **v0.2 Transport & Protocol Layer:** `BaseTransport` contract, `TCPTransport`, `SerialTransport`, `MockTransport`, `SCPIProtocol`, `VISAResourceManager`.
* [x] **v0.3 Instruments & Optical Simulation:** `OpticalPowerMeter`, `OpticalSwitch`, `OpticalOscilloscope`, `NetworkSwitch`, in-process TCP SCPI software simulators.
* [x] **v0.4 Python Test Automation Framework:** `conftest.py`, `assertions.py`, `helpers.py`, `reporting.py`, registered pytest markers.
* [x] **v0.5 Layer-2 Ethernet & Network Validation:** `MACAddress`, `VLANHeader`, `EthernetFrame`, `TrafficGenerator`, `TrafficSink`, `TrafficStatistics`.
* [x] **v0.6 C#/.NET Test Management & Orchestration:** Domain models (`TestCase`, `TestRun`, `TestResult`, `Device`, `Instrument`), REST controllers, `ApiExceptionMiddleware`, xUnit tests, `LabLinkAPIClient`.
* [x] **v0.7 PostgreSQL Persistence & Test Data Management:** `LabLinkDbContext`, `InitialPostgresSchema` EF Core migration, PostgreSQL repositories, Docker `postgres:15-alpine` container, persistence restart tests.
* [x] **v0.8 Jenkins + Shell CI/CD & Automated Quality Pipeline:** Declarative `Jenkinsfile`, POSIX shell scripts (`scripts/ci.sh`, `start_postgres.sh`, `migrate_database.sh`, `start_api.sh`, etc.), JUnit XML & TRX reports.
* [x] **v0.9 Containerized Full-Stack Deployment & Reproducible Environment:** Multi-stage `Dockerfile`, Docker Compose stack (`postgres` + `lablink-api`), container readiness health checks (`pg_isready`, `/api/v1/health`), named persistent volume (`lablink-postgres-data`), `./scripts/docker_up.sh`, `./scripts/docker_down.sh`, `./scripts/docker_smoke_test.sh`.
* [x] **v1.0 Manufacturing Test Execution, Measurement Traceability & Yield Analytics:** `DUT` model, versioned `TestSequence`, `TestStep`, `LimitEvaluator`, `VerdictEngine`, machine-readable `FailureCode`, `YieldAnalytics` (FPY vs final yield), `ManufacturingReporter`, `ManufacturingSimulationEngine` (100+ to 500+ DUT simulation), `run_demo.py`, `DutsController`, `ManufacturingController`, `AddManufacturingModels` EF Core migration, and complete quality gate verification.

---

## How to Run Manufacturing Simulation Demo

```bash
python -m lablink.manufacturing.run_demo --duts 100 --seed 42
```

---

## How to Run Containerized Full-Stack Environment

```bash
./scripts/docker_up.sh
./scripts/docker_migrate.sh
./scripts/docker_smoke_test.sh
./scripts/docker_down.sh
```

---

## How to Run Local CI Pipeline

```bash
./scripts/ci.sh
```
