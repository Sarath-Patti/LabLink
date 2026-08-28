# LabLink: Network & Instrument Test Automation Platform

LabLink is an extensible, multi-tier network and laboratory instrument test automation platform. It provides Python-based instrument control, networking transport abstractions, software Layer-2 Ethernet validation, and automated test execution alongside a C#/.NET 8 ASP.NET Core service layer for test management, run orchestration, PostgreSQL data persistence, and a declarative Jenkins + Shell CI/CD pipeline.

---

## Architecture Overview

LabLink employs a decoupled multi-tiered architecture:

* **Python Layer (`python/`):** Primary engine for test automation, physical/network transport handling (TCP/IP, Serial RS-232, Mock), SCPI protocol parsing, VISA-style resource management, instrument abstractions, optical equipment simulators, Layer-2 Ethernet frame modeling, 802.1Q VLAN tagging, software traffic generation/analysis, standard-library HTTP integration client (`LabLinkAPIClient`), and pytest-based test automation framework.
* **C# / .NET Layer (`dotnet/LabLink.Api` & `dotnet/LabLink.Api.Tests`):** Service layer providing an ASP.NET Core Web API orchestration foundation, domain models (`TestCase`, `TestRun`, `TestResult`, `Device`, `Instrument`), DTOs, application services, thin REST controllers, exception middleware, OpenAPI/Swagger documentation, and xUnit test suite.
* **Persistence Layer (`dotnet/LabLink.Api/Persistence`):** PostgreSQL Entity Framework Core 8.0 relational database persistence (`LabLinkDbContext`) supporting test run history, test results telemetry, device/instrument configuration, EF Core migrations (`InitialPostgresSchema`), and fallback thread-safe in-memory repositories.
* **CI/CD Pipeline (`Jenkinsfile` & `scripts/`):** Reproducible declarative Jenkins CI/CD pipeline and POSIX-compliant modular shell scripts automating static quality checks, unit/functional testing, Docker PostgreSQL service management, EF Core migrations, background API startup, and end-to-end HTTP smoke integration tests.

```
Developer / Git Push
        │
        ▼
   Jenkins CI/CD Pipeline (Jenkinsfile)
        │
        ├───────────────────────┐
        ▼                       ▼
 Python Quality Gate     .NET Build & xUnit
 (Ruff, Black, Mypy)     (dotnet build/format/test)
        │                       │
        └───────────┬───────────┘
                    ▼
          PostgreSQL Docker Service
                    │
                    ▼
            EF Core Migration
                    │
                    ▼
          PostgreSQL Integration
                    │
                    ▼
           REST API Startup
                    │
                    ▼
       Python API Smoke Test
                    │
                    ▼
       Artifacts & Log Cleanup
```

---

## Technology Stack

* **Automation & Drivers:** Python 3.11
* **Test Framework:** pytest (with markers, fixtures, custom assertions, JUnit XML output, and JSON telemetry export)
* **Networking & Layer-2 Validation:** Software EthernetFrame, MACAddress, 802.1Q VLANHeader, TrafficGenerator, TrafficSink, TrafficStatistics
* **Service API:** C# / .NET 8.0 ASP.NET Core Web API with OpenAPI/Swagger
* **API Test Framework:** xUnit, Microsoft.AspNetCore.Mvc.Testing WebApplicationFactory
* **ORM & Database:** Entity Framework Core 8.0, PostgreSQL 15 (`Npgsql.EntityFrameworkCore.PostgreSQL`)
* **Containers & Orchestration:** Docker Compose (`docker/docker-compose.yml`), PostgreSQL Alpine container
* **CI/CD & Shell Automation:** Jenkins Declarative Pipeline (`Jenkinsfile`), POSIX Bash (`scripts/`)

---

## Repository Structure

```
LabLink/
├── Jenkinsfile              # Declarative Jenkins CI/CD pipeline definition
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
│   │   └── integration/     # LabLinkAPIClient Python ↔ C# REST API integration client
│   └── tests/
│       ├── conftest.py      # Reusable fixtures (simulators, connected clients, L2 frames/traffic, config)
│       ├── unit/            # Unit tests for transports, SCPI, VISA, instruments, simulators, MAC, VLAN, Ethernet, traffic
│       ├── integration/     # TCP socket integration tests and Python ↔ C# REST API integration test
│       ├── functional/      # Functional tests for OPM, Switch, Scope, Network Switch, L2 frames
│       ├── regression/      # End-to-end multi-instrument & L2 network automated test bench regression suite
│       ├── negative/        # Negative boundary, invalid input, malformed MAC/VLAN, and error handling tests
│       ├── performance/     # SCPI query latency, measurement throughput, and L2 serialization/parsing benchmarks
│       └── utilities/       # Custom assertions, timing helpers, JSON result exporter
│
├── dotnet/
│   ├── LabLink.Api/         # ASP.NET Core Web API (Controllers, Services, Domain, Repositories, Persistence, Migrations)
│   └── LabLink.Api.Tests/   # Automated xUnit WebApplicationFactory & PostgreSQL integration test suite
│
├── docker/                  # Docker Compose PostgreSQL service definition
├── scripts/                 # Modular CI/CD shell scripts
│   ├── ci.sh                # Master local CI reproduction script
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

## Current Milestone Status

**Current Milestone:** `v0.8: Jenkins + Shell CI/CD & Automated Quality Pipeline`

### Implemented Functionality
* [x] **Repository Foundation (v0.1):** Python package, `.gitignore`, pytest setup, C# ASP.NET Core health service.
* [x] **Transport Architecture (v0.2):** Abstract `BaseTransport` contract with state management and timeouts.
* [x] **TCP/IP Transport (v0.2):** Real client `TCPTransport` socket implementation using standard library networking.
* [x] **RS-232 / Serial Transport (v0.2):** `SerialTransport` abstraction supporting baudrate/parity/stopbits and virtual backend fallback.
* [x] **Mock Transport (v0.2):** Deterministic `MockTransport` with request-response matching, read queues, custom handlers, and timeout/error injection.
* [x] **SCPI Protocol Layer (v0.2):** `SCPIProtocol` supporting IEEE 488.2 common commands (`*IDN?`, `*RST`, `*CLS`, `SYST:ERR?`) and response parsing helpers.
* [x] **VISA-Style Resource Abstraction (v0.2):** `VISAResourceManager` and `VISAResource` parsing descriptors (`TCPIP`, `ASRL`, `MOCK`) without external NI-VISA C-binary dependencies.
* [x] **Instrument Abstraction Layer (v0.3):** `BaseInstrument` composing transport and protocol objects via dependency injection.
* [x] **Optical Equipment & Device Control (v0.3):** `OpticalPowerMeter`, `OpticalSwitch`, `OpticalOscilloscope`, and `NetworkSwitch`.
* [x] **Software Simulators Layer (v0.3):** Local TCP SCPI server simulators (`OpticalPowerMeterSimulator`, `OpticalSwitchSimulator`, `OpticalOscilloscopeSimulator`, `NetworkSwitchSimulator`) listening on `127.0.0.1`.
* [x] **Layer-2 MAC Address Model (v0.5):** `MACAddress` supporting string parsing (colon, hyphen, raw hex), canonical string output, byte conversion, broadcast/multicast classification.
* [x] **IEEE 802.1Q VLAN Tagging (v0.5):** `VLANHeader` supporting VLAN ID validation (`0..4095`), Priority Code Point (`0..7`), DEI flags, and 4-byte TCI binary serialization/parsing.
* [x] **Ethernet Frame Abstraction (v0.5):** `EthernetFrame` supporting untagged and 802.1Q tagged frame modeling, embedded telemetry headers (sequence IDs, nanosecond timestamps), frame padding, binary serialization, and deserialization.
* [x] **Software Traffic Generator & Sink (v0.5):** `TrafficGenerator` and `TrafficSink` with `TrafficStatistics` telemetry.
* [x] **Pytest Framework & Markers (v0.4/v0.5):** Registered `l2`, `functional`, `regression`, `negative`, `performance`, `instrument`, `simulator`, `integration` markers.
* [x] **C# ASP.NET Core Test Orchestration API (v0.6):** Domain models (`TestCase`, `TestRun`, `TestResult`, `Device`, `Instrument`), DTOs, application services, thin REST controllers.
* [x] **Test Run Lifecycle & Ingestion (v0.6):** Lifecycle state machine (`Created` -> `Running` -> `Completed`) with automatic result aggregation metrics calculation.
* [x] **API Error Middleware & OpenAPI (v0.6):** `ApiExceptionMiddleware` mapping domain exceptions to structured JSON errors (`400`, `404`, `409`, `500`) and Swagger UI.
* [x] **C# xUnit API Test Suite (v0.6):** `LabLink.Api.Tests` using `WebApplicationFactory` covering health, test case, test run lifecycle, result ingestion, device, and instrument endpoints.
* [x] **Python ↔ C# HTTP Integration Client & Test (v0.6):** `LabLinkAPIClient` standard library client and `test_api_integration.py` workflow test.
* [x] **PostgreSQL Database Persistence (v0.7):** `LabLinkDbContext` with EF Core 8.0 relational tables, indexes, and JSON dictionary metadata conversion.
* [x] **PostgreSQL Repositories (v0.7):** `PostgresTestCaseRepository`, `PostgresTestRunRepository`, `PostgresTestResultRepository`, `PostgresDeviceRepository`, `PostgresInstrumentRepository` with DI provider switching.
* [x] **Docker PostgreSQL Service (v0.7):** `docker/docker-compose.yml` (`postgres:15-alpine`) with persistent volume.
* [x] **PostgreSQL Integration Test Suite (v0.7):** xUnit `PostgresRepositoryIntegrationTests` verifying migrations, relational integrity, JSON metadata, and restart persistence.
* [x] **Declarative Jenkins Pipeline (v0.8):** Root `Jenkinsfile` orchestrating automated quality stages, test report collection, and post-build cleanup.
* [x] **Modular CI/CD Shell Scripts (v0.8):** POSIX-compliant bash scripts under `scripts/` (`setup_python.sh`, `start_postgres.sh`, `wait_for_postgres.sh`, `migrate_database.sh`, `start_api.sh`, `run_python_quality.sh`, `run_python_tests.sh`, `run_dotnet_tests.sh`, `run_integration_tests.sh`, `cleanup.sh`, `ci.sh`).
* [x] **Local CI Master Script (v0.8):** `./scripts/ci.sh` for reproducing the full Jenkins pipeline locally in a single command.

---

## How to Run Local CI Pipeline

Run the local master CI script to execute the complete pipeline locally:

```bash
./scripts/ci.sh
```

---

## How to Run Individual Quality Gates

### Python Static Quality Checks
```bash
./scripts/run_python_quality.sh
```

### Python Pytest Automation Framework
```bash
./scripts/run_python_tests.sh
```

### C# .NET Build, Formatting & xUnit Tests
```bash
./scripts/run_dotnet_tests.sh
```

### PostgreSQL Database & EF Core Migrations
```bash
./scripts/start_postgres.sh
./scripts/wait_for_postgres.sh
./scripts/migrate_database.sh
```

### API Service & Integration Smoke Test
```bash
./scripts/start_api.sh
./scripts/run_integration_tests.sh
./scripts/cleanup.sh
```

---

## Maintenance & Cleanup

To remove background API processes, stop Docker containers, and clean temporary log files:

```bash
./scripts/cleanup.sh
```
