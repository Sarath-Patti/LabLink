# LabLink: Network & Instrument Test Automation Platform

LabLink is an extensible, multi-tier network and laboratory instrument test automation platform. It provides Python-based instrument control, networking transport abstractions, and automated test execution alongside a C#/.NET service layer for test management.

---

## Architecture Overview

LabLink employs a decoupled multi-tiered architecture:

* **Python Layer (`python/`):** Primary engine for test automation, physical/network transport handling (TCP/IP, Serial RS-232, Mock), SCPI protocol parsing, VISA-style resource management, instrument abstractions, optical equipment simulators, hardware device control, and pytest-based test automation framework.
* **C# / .NET Layer (`dotnet/LabLink.Api`):** Service layer providing an ASP.NET Core Web API foundation for test management, run orchestration, and reporting.
* **Persistence Layer (Planned):** PostgreSQL database integration for historical test logs, device telemetry, and run results.
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
* **Service API:** C# / .NET 8.0 ASP.NET Core
* **Networking & Protocols:** TCP/IP Sockets, RS-232 Serial, SCPI (IEEE 488.2), VISA-style abstractions
* **Instruments & Simulators:** Optical Power Meter, Optical Switch, Optical Oscilloscope, Network Switch Control
* **Persistence (Planned):** PostgreSQL
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
│   │   └── simulators/      # BaseInstrumentSimulator, OpticalPowerMeterSimulator, OpticalSwitchSimulator, OpticalOscilloscopeSimulator, NetworkSwitchSimulator
│   └── tests/
│       ├── conftest.py      # Reusable fixtures (simulators, connected clients, config)
│       ├── unit/            # Unit tests for transports, SCPI, VISA, instruments, simulators
│       ├── integration/     # Local TCP socket integration tests against local simulators
│       ├── functional/      # Functional tests for OPM, Switch, Scope, Network Switch
│       ├── regression/      # End-to-end multi-instrument automated test bench regression suite
│       ├── negative/        # Negative boundary, invalid input, and error handling tests
│       ├── performance/     # SCPI query latency and measurement throughput benchmarks
│       └── utilities/       # Custom assertions, timing helpers, JSON result exporter
│
├── dotnet/
│   └── LabLink.Api/         # ASP.NET Core Web API foundation
│
├── config/                  # Safe configuration templates (.json, .env)
├── docs/                    # Architectural & design documentation
├── scripts/                 # Development lifecycle scripts (setup, test, clean)
├── ethernet/                # Layer-2 Ethernet test components (Milestone v0.5)
├── docker/                  # Docker containerization (Milestone v0.6)
└── jenkins/                 # Jenkins CI/CD pipelines (Milestone v0.6)
```

---

## Current Milestone Status

**Current Milestone:** `v0.4: Python Test Automation Framework`

### Implemented Functionality
* [x] **Repository Foundation:** Python package, `.gitignore`, pytest setup, C# ASP.NET Core health service.
* [x] **Transport Architecture:** Abstract `BaseTransport` contract with state management and timeouts.
* [x] **TCP/IP Transport:** Real client `TCPTransport` socket implementation using standard library networking.
* [x] **RS-232 / Serial Transport:** `SerialTransport` abstraction supporting baudrate/parity/stopbits and virtual backend fallback.
* [x] **Mock Transport:** Deterministic `MockTransport` with request-response matching, read queues, custom handlers, and timeout/error injection.
* [x] **SCPI Protocol Layer:** `SCPIProtocol` supporting IEEE 488.2 common commands (`*IDN?`, `*RST`, `*CLS`, `SYST:ERR?`) and response parsing helpers.
* [x] **VISA-Style Resource Abstraction:** `VISAResourceManager` and `VISAResource` parsing descriptors (`TCPIP`, `ASRL`, `MOCK`) without external NI-VISA C-binary dependencies.
* [x] **Instrument Abstraction Layer:** `BaseInstrument` composing transport and protocol objects via dependency injection.
* [x] **Optical Equipment & Device Control:** `OpticalPowerMeter`, `OpticalSwitch`, `OpticalOscilloscope`, and `NetworkSwitch`.
* [x] **Software Simulators Layer:** Local TCP SCPI server simulators (`OpticalPowerMeterSimulator`, `OpticalSwitchSimulator`, `OpticalOscilloscopeSimulator`, `NetworkSwitchSimulator`) listening on `127.0.0.1`.
* [x] **Reusable Pytest Fixtures:** Dynamic simulator lifecycle (`opm_sim`, `switch_sim`, `scope_sim`, `net_switch_sim`) and connected client fixtures (`opm_client`, `switch_client`, `scope_client`, `net_switch_client`).
* [x] **Standardized Pytest Markers:** Registered `functional`, `regression`, `negative`, `performance`, `instrument`, `simulator` markers.
* [x] **Functional Test Suite:** Parameterized test cases for wavelength tuning, power units, optical switch routing, timebase scaling, and port control.
* [x] **Regression Test Suite:** End-to-end multi-instrument optical test bench workflow verification.
* [x] **Negative Test Suite:** Out-of-range parameters, disabled acquisition errors, undefined SCPI headers, and transport disconnection modes.
* [x] **Performance Benchmarks:** Empirical SCPI query round-trip latency and measurement throughput benchmarking with JSON result telemetry exports.
* [x] **Custom Assertion Helpers:** `assert_within_tolerance`, `assert_greater_than`, `assert_less_than`, and `assert_in_range`.
* [x] **Structured Test Results:** `TestMeasurementResult` dataclass and `JSONResultExporter` generating `test_results.json`.

### Explicitly Deferred / Planned Functionality
* [ ] Physical optical equipment validation (No physical optical hardware attached)
* [ ] NI-VISA native binary C-driver bindings (VISA-style software abstraction implemented)
* [ ] IXIA hardware integration (Deferred)
* [ ] Layer-2 Ethernet raw packet generation, VLAN forwarding & traffic generator — *Milestone v0.5*
* [ ] PostgreSQL database persistence & schema migrations — *Milestone v0.5*
* [ ] ASP.NET Core test management REST API endpoints — *Milestone v0.5*
* [ ] Docker environment & Jenkins CI/CD automation — *Milestone v0.6*

---

## How to Set Up the Python Environment

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

---

## How to Run the Pytest Automation Framework

Run all or selective test suites within the `python` directory:

```bash
cd python

# Run entire test suite
pytest -v

# Run selective test directories
pytest tests/functional -v
pytest tests/regression -v
pytest tests/negative -v
pytest tests/performance -v

# Run selective marker suites
pytest -m functional -v
pytest -m regression -v
pytest -m negative -v
pytest -m performance -v
```

---

## How to Start the .NET API Foundation

1. Ensure .NET 8.0 SDK is installed.
2. Navigate to the API project directory:
   ```bash
   cd dotnet/LabLink.Api
   ```
3. Run the Web API application:
   ```bash
   dotnet run
   ```
4. Access the health status endpoint at `http://localhost:5000/api/v1/health`.

---

## Maintenance & Cleanup

To remove temporary build output, Python byte-code caches, and .NET compilation artifacts:

```bash
./scripts/clean.sh
```
