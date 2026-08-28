# LabLink High-Level System Architecture

## Architecture Overview

LabLink is a multi-tier network and laboratory instrument test automation platform designed with strict separation of concerns across technical stacks:

1. **Python Layer (`python/`)**
   * **Role:** Primary test automation engine, instrument integration, protocol parsing, hardware transport execution, Layer-2 Ethernet validation, software traffic generation, standard-library HTTP API client (`LabLinkAPIClient`), and pytest automation framework.
   * **Responsibility:** Executes SCPI commands, manages TCP/IP, RS-232 serial, and Layer-2 Ethernet streams, drives instrument drivers, software simulators, software traffic engines, and runs pytest automation workflows.

2. **C#/.NET Layer (`dotnet/LabLink.Api` & `dotnet/LabLink.Api.Tests`)**
   * **Role:** Test management, orchestration, and external Web API platform.
   * **Responsibility:** Manages test case definitions, test run lifecycles, test result ingestion, device/instrument metadata, exposes REST endpoints (`/api/v1/`), provides OpenAPI/Swagger documentation, and maintains EF Core PostgreSQL database persistence.

3. **Persistence Layer (`dotnet/LabLink.Api/Persistence`)**
   * **Role:** Relational database storage and schema migration.
   * **Responsibility:** `LabLinkDbContext` with EF Core 8.0 mapping `TestCase`, `TestRun`, `TestResult`, `Device`, and `Instrument` entities to PostgreSQL.

4. **CI/CD Pipeline (`Jenkinsfile` & `scripts/`)**
   * **Role:** Automated quality verification and pipeline orchestration.
   * **Responsibility:** Declarative Jenkins pipeline and POSIX-compliant modular shell scripts executing static analysis, testing, PostgreSQL service startup, database migration, API startup, and end-to-end integration smoke testing.

```
                  +-----------------------------------+
                  |      C# / ASP.NET Core API        |
                  |     (Test Management & API)       |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------------------------+
                  |     Python Automation Engine      |
                  |   (Instrument Control & pytest)   |
                  +-----------------+-----------------+
                                    |
        +---------------------------+---------------------------+
        |                           |                           |
        v                           v                           v
+---------------+           +---------------+           +---------------+
|  TCP/IP /     |           |   SCPI /      |           |   Layer-2     |
| Serial RS232  |           |  Instrument   |           |   Ethernet    |
| Transport     |           |  Protocols    |           |   Testing     |
+---------------+           +---------------+           +---------------+
```

---

## Milestone v0.8 Jenkins + Shell CI/CD Pipeline Architecture

```
Developer / Git Push
        │
        ▼
   Jenkins CI/CD Pipeline (Jenkinsfile)
        │
        ├────────────────────────┬────────────────────────┐
        ▼                        ▼                        ▼
 Python Quality Gate      Python Pytest Suite     .NET Build/Format/xUnit
 (Ruff, Black, Mypy)     (JUnit XML Output)       (.trx Output)
        │                        │                        │
        └────────────────────────┼────────────────────────┘
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
                   Python API Smoke Integration
                                 │
                                 ▼
                      Artifacts & Log Cleanup
```

### 1. Declarative Pipeline Stages (`Jenkinsfile`)
- **Checkout:** Source code retrieval from Git SCM.
- **Environment Validation:** Verifies system python, dotnet SDK, bash, and docker binaries.
- **Setup Python Environment:** Isolated venv initialization via `./scripts/setup_python.sh`.
- **Python Quality:** Runs `./scripts/run_python_quality.sh` (`ruff`, `black`, `mypy`).
- **Python Tests:** Runs `./scripts/run_python_tests.sh` with JUnit XML report output.
- **.NET Quality & Tests:** Runs `./scripts/run_dotnet_tests.sh` (`dotnet build`, `dotnet format`, `dotnet test`).
- **PostgreSQL & Migrations:** Runs `./scripts/start_postgres.sh`, `./scripts/wait_for_postgres.sh`, and `./scripts/migrate_database.sh`.
- **API Integration & Smoke Test:** Runs `./scripts/start_api.sh` and `./scripts/run_integration_tests.sh`.
- **Packaging & Cleanup:** Archives JUnit XML test reports, TRX test files, and API log files. Post block executes `./scripts/cleanup.sh`.

### 2. POSIX Shell Script Inventory (`scripts/`)
- **`ci.sh`**: Master local CI runner executing all quality gates sequentially.
- **`setup_python.sh`**: Environment initialization and package installation.
- **`run_python_quality.sh`**: Linter and type checker execution.
- **`run_python_tests.sh`**: Pytest test suite execution.
- **`run_dotnet_tests.sh`**: .NET compilation, formatting, and unit testing.
- **`start_postgres.sh`**: Docker container container startup.
- **`wait_for_postgres.sh`**: PostgreSQL connection polling loop.
- **`migrate_database.sh`**: EF Core migration application (`dotnet ef database update`).
- **`start_api.sh`**: Background API process startup, PID recording (`.api.pid`), and health polling.
- **`run_integration_tests.sh`**: Python ↔ C# REST API smoke workflow execution.
- **`cleanup.sh`**: Background process termination and Docker service shutdown.

---

## Milestone v0.7 PostgreSQL Persistence Architecture

### 1. EF Core Database Context & Provider Switching
`LabLinkDbContext` manages relational persistence for test entities. `Program.cs` reads `Persistence:Provider` configuration:
- `"PostgreSQL"`: Registers `LabLinkDbContext` with `options.UseNpgsql(...)` and scoped PostgreSQL repositories.
- `"InMemory"`: Registers thread-safe in-memory repositories.

### 2. Telemetry Protection & Relationships
- `TestRun` 1 $\rightarrow$ * `TestResult`: Foreign key configured with `DeleteBehavior.Restrict` to protect historical test telemetry from accidental cascade deletion.
- `Device.Metadata`: Values converted to JSON strings using `System.Text.Json` value converters.

---

## Milestone v0.6 C#/.NET Service Layer Architecture

### 1. Component Separation
$$\text{Python pytest / HTTP Client} \longrightarrow \text{REST Controllers} \longrightarrow \text{Application Services} \longrightarrow \text{Domain Models} \longrightarrow \text{Repositories}$$

---

## Milestone v0.5 Layer-2 Ethernet & Network Validation Architecture

### 1. Subsystem Composition (`lablink.network`)
$$\text{TrafficGenerator} \longrightarrow \text{EthernetFrame (MACAddress + VLANHeader)} \longrightarrow \text{TrafficSink} \longrightarrow \text{TrafficStatistics}$$

---

## Milestone v0.3 Instrument & Simulator Subsystems

### 1. Layered Interface Composition Pattern
$$\text{Instrument / Device Driver} \longrightarrow \text{SCPI Protocol} \longrightarrow \text{BaseTransport} \longrightarrow \text{TCP Simulator (127.0.0.1)}$$

---

## Implementation Status (Milestone v0.8)

### Implemented Functionality
* [x] Abstract transport interface contract (`BaseTransport`) & client transports (`TCPTransport`, `SerialTransport`, `MockTransport`)
* [x] SCPI protocol handler (`SCPIProtocol`) & IEEE 488.2 common commands (`*IDN?`, `*RST`, `*CLS`, `SYST:ERR?`)
* [x] VISA-style resource manager (`VISAResourceManager`) & resource wrapper (`VISAResource`)
* [x] Base instrument abstraction (`BaseInstrument`) & concrete instrument drivers (`OpticalPowerMeter`, `OpticalSwitch`, `OpticalOscilloscope`, `NetworkSwitch`)
* [x] In-process TCP SCPI software simulators (`OpticalPowerMeterSimulator`, `OpticalSwitchSimulator`, `OpticalOscilloscopeSimulator`, `NetworkSwitchSimulator`)
* [x] Layer-2 MAC address value object (`MACAddress`) & 802.1Q VLAN tag model (`VLANHeader`)
* [x] Ethernet MAC frame modeling (`EthernetFrame`) & telemetry header embedding (sequence numbers, timestamps)
* [x] Software traffic generator (`TrafficGenerator`) & software traffic receiver/sink (`TrafficSink`)
* [x] Traffic performance statistics engine (`TrafficStatistics`)
* [x] Pytest test automation framework structure & markers (`l2`, `functional`, `regression`, `negative`, `performance`, `instrument`, `simulator`, `integration`)
* [x] C# ASP.NET Core Web API orchestration layer (`Controllers`, `Services`, `Domain`, `Repositories`, `Middleware`)
* [x] Thread-safe in-memory repository abstractions (`ConcurrentDictionary`)
* [x] Test-run lifecycle management & result ingestion metrics aggregation
* [x] Structured API exception middleware (`ApiExceptionMiddleware`) & OpenAPI/Swagger documentation
* [x] C# xUnit API test suite (`LabLink.Api.Tests`) using `WebApplicationFactory`
* [x] Python standard-library HTTP API client (`LabLinkAPIClient`) & Python ↔ C# REST API integration test suite
* [x] PostgreSQL database persistence (`LabLinkDbContext`) & EF Core migrations (`InitialPostgresSchema`)
* [x] PostgreSQL repositories (`PostgresTestCaseRepository`, `PostgresTestRunRepository`, etc.)
* [x] Docker PostgreSQL service definition (`docker/docker-compose.yml`) & environment template (`.env.example`)
* [x] Declarative Jenkins CI/CD pipeline (`Jenkinsfile`) & test report collection
* [x] POSIX-compliant modular shell scripts (`scripts/*.sh`) & local CI master script (`scripts/ci.sh`)
* [x] Hardware-free unit, integration, functional, regression, negative, performance, and CI/CD quality gate suites

### Deliberately Deferred Functionality (Future Milestones)
* [ ] Physical optical equipment validation (No physical optical hardware attached)
* [ ] NI-VISA native binary driver bindings — *Deferred*
* [ ] IXIA hardware integration — *Deferred*
* [ ] Kernel-bypass networking / DPDK drivers — *Deferred*
* [ ] Kubernetes / ArgoCD deployment — *Deferred*
