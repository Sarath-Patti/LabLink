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

5. **Containerized Deployment Layer (`docker/` & `dotnet/LabLink.Api/Dockerfile`)**
   * **Role:** Multi-service container orchestration and reproducible deployment.
   * **Responsibility:** Multi-stage Dockerfile packaging `LabLink.Api` into a lightweight runtime image; Docker Compose orchestrating `postgres` and `lablink-api` with native health checks (`pg_isready`, `/api/v1/health`) and named persistent volume storage (`lablink-postgres-data`).

```
                    Developer / Jenkins
                           │
                           ▼
                    Docker Compose
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
      ┌───────────────┐         ┌───────────────┐
      │ LabLink API   │────────▶│ PostgreSQL    │
      │ ASP.NET Core  │         │ Database      │
      └───────────────┘         └───────────────┘
              │                         │
              │                         ▼
              │                   Persistent
              │                     Volume
              │             (lablink-postgres-data)
              ▼
       Python Automation /
       Integration Tests
```

---

## Milestone v0.9 Containerized Full-Stack Deployment Architecture

### 1. Multi-Stage Docker Build (`dotnet/LabLink.Api/Dockerfile`)
* **Stage 1 (SDK 8.0):** Compiles project, restores NuGet dependencies, publishes Release binaries.
* **Stage 2 (ASP.NET 8.0 Runtime):** Minimal footprint runtime container exposing port `5099` with internal healthcheck (`curl http://localhost:5099/api/v1/health`).

### 2. Multi-Service Orchestration (`docker/docker-compose.yml`)
* **Service `postgres`**: `postgres:15-alpine` image with container healthcheck `pg_isready -U sarathpatti -d lablink_dev` and persistent named volume `lablink-postgres-data`.
* **Service `lablink-api`**: Built from multi-stage Dockerfile, depends on `postgres: service_healthy`, environment-configured connection string `Host=postgres;Port=5432;Database=lablink_dev`.
* **Host Access**: API port `5099` and PostgreSQL port `5432` mapped to host for pytest automation framework execution and local API testing.

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

---

## Milestone v0.7 PostgreSQL Persistence Architecture

### 1. EF Core Database Context & Provider Switching
`LabLinkDbContext` manages relational persistence for test entities. `Program.cs` reads `Persistence:Provider` configuration:
- `"PostgreSQL"`: Registers `LabLinkDbContext` with `options.UseNpgsql(...)` and scoped PostgreSQL repositories.
- `"InMemory"`: Registers thread-safe in-memory repositories.

---

## Milestone v0.6 C#/.NET Service Layer Architecture

### 1. Component Separation
$$\text{Python pytest / HTTP Client} \longrightarrow \text{REST Controllers} \longrightarrow \text{Application Services} \longrightarrow \text{Domain Models} \longrightarrow \text{Repositories}$$

---

## Implementation Status (Milestone v0.9)

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
* [x] Declarative Jenkins CI/CD pipeline (`Jenkinsfile`) & test report collection
* [x] POSIX-compliant modular shell scripts (`scripts/*.sh`) & local CI master script (`scripts/ci.sh`)
* [x] Multi-Stage Dockerfile (`dotnet/LabLink.Api/Dockerfile`) targeting lightweight ASP.NET 8.0 runtime image
* [x] Multi-Service Docker Compose Stack (`docker/docker-compose.yml`) orchestrating `postgres` and `lablink-api` with health checks (`pg_isready`, `/api/v1/health`) and named persistent volume `lablink-postgres-data`
* [x] Docker Management Suite (`./scripts/docker_up.sh`, `./scripts/docker_down.sh`, `./scripts/docker_migrate.sh`, `./scripts/docker_smoke_test.sh`)

### Deliberately Deferred Functionality (Future Milestones)
* [ ] Physical optical equipment validation (No physical optical hardware attached)
* [ ] NI-VISA native binary driver bindings — *Deferred*
* [ ] IXIA hardware integration — *Deferred*
* [ ] Kernel-bypass networking / DPDK drivers — *Deferred*
* [ ] Kubernetes / ArgoCD deployment — *Deferred*
