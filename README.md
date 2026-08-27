# LabLink: Network & Instrument Test Automation Platform

LabLink is an extensible, multi-tier network and laboratory instrument test automation platform. It provides Python-based instrument control, networking transport abstractions, and automated test execution alongside a C#/.NET service layer for test management.

---

## Architecture Overview

LabLink employs a decoupled multi-tiered architecture:

* **Python Layer (`python/`):** Primary engine for test automation, physical/network transport handling (TCP/IP, Serial RS-232, Mock), SCPI protocol parsing, VISA-style resource management, instrument abstractions, optical equipment simulators, and hardware device control.
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
* **Test Framework:** pytest
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
│       ├── unit/            # Unit tests for transports, SCPI, VISA, instruments, simulators
│       └── integration/     # Local TCP socket integration tests against local simulators
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

**Current Milestone:** `v0.3: Instruments & Optical Simulation`

### Implemented Functionality
* [x] **Repository Foundation:** Python package, `.gitignore`, pytest setup, C# ASP.NET Core health service.
* [x] **Transport Architecture:** Abstract `BaseTransport` contract with state management and timeouts.
* [x] **TCP/IP Transport:** Real client `TCPTransport` socket implementation using standard library networking.
* [x] **RS-232 / Serial Transport:** `SerialTransport` abstraction supporting baudrate/parity/stopbits and virtual backend fallback.
* [x] **Mock Transport:** Deterministic `MockTransport` with request-response matching, read queues, custom handlers, and timeout/error injection.
* [x] **SCPI Protocol Layer:** `SCPIProtocol` supporting IEEE 488.2 common commands (`*IDN?`, `*RST`, `*CLS`, `SYST:ERR?`) and response parsing helpers.
* [x] **VISA-Style Resource Abstraction:** `VISAResourceManager` and `VISAResource` parsing descriptors (`TCPIP`, `ASRL`, `MOCK`) without external NI-VISA C-binary dependencies.
* [x] **Instrument Abstraction Layer:** `BaseInstrument` composing transport and protocol objects via dependency injection.
* [x] **Optical Power Meter:** `OpticalPowerMeter` supporting wavelength configuration (`CONF:WAVELENGTH`), unit selection (`CONF:UNIT`), and power measurement (`MEAS:POW?`).
* [x] **Optical Switch:** `OpticalSwitch` supporting channel routing (`ROUTE:SET`), route queries (`ROUTE?`), and channel count inspection.
* [x] **Optical Oscilloscope:** `OpticalOscilloscope` supporting timebase scale (`TIMEBASE:SCALE`), channel scale (`CHANNEL:SCALE`), acquisition state (`ACQUIRE:STATE`), and structured `WaveformData` acquisition.
* [x] **Network Switch Device Abstraction:** `NetworkSwitch` supporting port state management (`enable_port`, `disable_port`, `get_port_state`, `get_all_port_states`).
* [x] **Software Simulators Layer:** Thread-safe local TCP SCPI simulators (`OpticalPowerMeterSimulator`, `OpticalSwitchSimulator`, `OpticalOscilloscopeSimulator`, `NetworkSwitchSimulator`) listening on `127.0.0.1` with FIFO error queue support (`SYST:ERR?`).
* [x] **Error Model:** Hierarchical domain exceptions (`TransportConnectionError`, `TransportTimeoutError`, `TransportIOError`, `SCPIError`, `VISAError`, `InvalidResponseError`).
* [x] **Automated Tests:** Hardware-free unit tests and end-to-end local TCP integration tests.

### Explicitly Deferred / Planned Functionality
* [ ] Physical optical equipment validation (No physical optical hardware attached)
* [ ] NI-VISA native binary C-driver bindings (VISA-style software abstraction implemented)
* [ ] IXIA hardware integration (Deferred)
* [ ] Layer-2 Ethernet raw packet generation, VLAN forwarding & traffic generator — *Milestone v0.5*
* [ ] PostgreSQL database persistence & schema migrations — *Milestone v0.4*
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

## How to Run the Pytest Infrastructure

Run the test suite using the project test script or directly via `pytest`:

```bash
# Option 1: Using the provided script
./scripts/run_tests.sh

# Option 2: Running pytest directly within the python directory
cd python
pytest -v
```

The test suite includes unit tests for TCP, Serial, Mock transports, SCPI protocol formatting, VISA descriptors, instruments, device abstractions, software simulators, and local in-process TCP socket integration tests.

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
