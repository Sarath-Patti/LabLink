# LabLink: Network & Instrument Test Automation Platform

LabLink is an extensible, multi-tier network and laboratory instrument test automation platform. It provides Python-based instrument control, networking transport abstractions, software Layer-2 Ethernet validation, and automated test execution alongside a C#/.NET 8 ASP.NET Core service layer for test management, run orchestration, and result ingestion.

---

## Architecture Overview

LabLink employs a decoupled multi-tiered architecture:

* **Python Layer (`python/`):** Primary engine for test automation, physical/network transport handling (TCP/IP, Serial RS-232, Mock), SCPI protocol parsing, VISA-style resource management, instrument abstractions, optical equipment simulators, Layer-2 Ethernet frame modeling, 802.1Q VLAN tagging, software traffic generation/analysis, standard-library HTTP integration client (`LabLinkAPIClient`), and pytest-based test automation framework.
* **C# / .NET Layer (`dotnet/LabLink.Api` & `dotnet/LabLink.Api.Tests`):** Service layer providing an ASP.NET Core Web API orchestration foundation, domain models (`TestCase`, `TestRun`, `TestResult`, `Device`, `Instrument`), DTOs, application services, thin REST controllers, exception middleware, OpenAPI/Swagger documentation, and xUnit test suite.
* **In-Memory Storage (v0.6):** Thread-safe in-memory repositories (`ConcurrentDictionary`) managing transient test runs, results, and device metadata.
* **Persistence Layer (Planned - v0.7):** PostgreSQL database integration for historical test logs, device telemetry, and run results.
* **Infrastructure (Planned):** Docker-based integration environments and Jenkins CI/CD automation pipelines.

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

## Technology Stack

* **Automation & Drivers:** Python 3.11
* **Test Framework:** pytest (with markers, fixtures, custom assertions, and JSON telemetry export)
* **Networking & Layer-2 Validation:** Software EthernetFrame, MACAddress, 802.1Q VLANHeader, TrafficGenerator, TrafficSink, TrafficStatistics
* **Service API:** C# / .NET 8.0 ASP.NET Core Web API with OpenAPI/Swagger
* **API Test Framework:** xUnit, Microsoft.AspNetCore.Mvc.Testing WebApplicationFactory
* **Instruments & Simulators:** Optical Power Meter, Optical Switch, Optical Oscilloscope, Network Switch Control
* **Persistence (v0.6):** In-Memory Repositories (PostgreSQL deferred to v0.7)
* **CI/CD & Containers (Planned):** Docker, Jenkins

---

## Repository Structure

```
LabLink/
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
│   ├── LabLink.Api/         # ASP.NET Core Web API (Controllers, Services, Domain, Repositories, Middleware)
│   └── LabLink.Api.Tests/   # Automated xUnit WebApplicationFactory test suite
│
├── config/                  # Safe configuration templates (.json, .env)
├── docs/                    # Architectural & design documentation
├── scripts/                 # Development lifecycle scripts (setup, test, clean)
├── ethernet/                # Layer-2 Ethernet test components
├── docker/                  # Docker containerization (Milestone v0.8)
└── jenkins/                 # Jenkins CI/CD pipelines (Milestone v0.8)
```

---

## Current Milestone Status

**Current Milestone:** `v0.6: C#/.NET Test Management & Orchestration`

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
* [x] **In-Memory Repositories (v0.6):** Thread-safe in-memory repositories managing test runs, test cases, test results, devices, and instruments.
* [x] **Test Run Lifecycle & Ingestion (v0.6):** Lifecycle state machine (`Created` -> `Running` -> `Completed`) with automatic result aggregation metrics calculation.
* [x] **API Error Middleware & OpenAPI (v0.6):** `ApiExceptionMiddleware` mapping domain exceptions to structured JSON errors (`400`, `404`, `409`, `500`) and Swagger UI.
* [x] **C# xUnit API Test Suite (v0.6):** `LabLink.Api.Tests` using `WebApplicationFactory` covering health, test case, test run lifecycle, result ingestion, device, and instrument endpoints.
* [x] **Python ↔ C# HTTP Integration Client & Test (v0.6):** `LabLinkAPIClient` standard library client and `test_api_integration.py` workflow test.

### Explicitly Deferred / Planned Functionality
* [ ] PostgreSQL database persistence & schema migrations — *Milestone v0.7*
* [ ] Physical optical equipment validation (No physical optical hardware attached)
* [ ] NI-VISA native binary C-driver bindings (VISA-style software abstraction implemented)
* [ ] IXIA hardware generator integration (Deferred)
* [ ] Kernel-bypass networking / DPDK drivers (Deferred)
* [ ] Docker environment & Jenkins CI/CD automation — *Milestone v0.8*

---

## How to Set Up the Environment

### Python Environment
1. Navigate to the `python` directory or use the provided setup script:
   ```bash
   ./scripts/setup.sh
   ```
2. Activate the virtual environment:
   ```bash
   source python/.venv/bin/activate
   ```
3. Install development dependencies in editable mode:
   ```bash
   pip install -e "python/[dev]"
   ```

### .NET Environment
1. Ensure .NET 8.0 SDK is installed.
2. Build the C# solution/projects:
   ```bash
   cd dotnet/LabLink.Api
   dotnet build
   ```

---

## How to Run Verification Suites

### Python Pytest Automation Framework
```bash
cd python

# Run entire test suite
pytest -v

# Run selective marker suites
pytest -m l2 -v
pytest -m functional -v
pytest -m regression -v
pytest -m negative -v
pytest -m performance -v
pytest -m integration -v
```

### C# .NET Automated xUnit Test Suite
```bash
cd dotnet/LabLink.Api.Tests
dotnet test
```

### .NET Formatting Verification
```bash
cd dotnet/LabLink.Api
dotnet format --verify-no-changes
```

---

## How to Start the C# ASP.NET Core API

1. Navigate to the API project directory:
   ```bash
   cd dotnet/LabLink.Api
   ```
2. Run the Web API application:
   ```bash
   dotnet run
   ```
3. Access the health status endpoint at `http://localhost:5000/api/v1/health`.
4. Access Swagger UI documentation at `http://localhost:5000/swagger`.

---

## Maintenance & Cleanup

To remove temporary build output, Python byte-code caches, and .NET compilation artifacts:

```bash
./scripts/clean.sh
```
