# LabLink High-Level System Architecture

## Architecture Overview

LabLink is a multi-tier network and laboratory instrument test automation platform designed with strict separation of concerns across two primary technical stacks:

1. **Python Layer (`python/`)**
   * **Role:** Primary test automation engine, instrument integration, protocol parsing, hardware transport execution, and pytest automation framework.
   * **Responsibility:** Executes SCPI commands, manages TCP/IP, RS-232 serial, and Layer-2 Ethernet streams, drives instrument drivers, software simulators, and runs pytest automation workflows.

2. **C#/.NET Layer (`dotnet/LabLink.Api`)**
   * **Role:** Test management, orchestration, and external Web API platform.
   * **Responsibility:** Manages test run schedules, exposes REST endpoints for test status, aggregates telemetry, and coordinates persistence via PostgreSQL.

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

## Milestone v0.4 Test Automation Framework Architecture

### 1. Test Layer Composition & Selective Execution Map
The test framework organizes tests into explicit, modular directories and pytest markers to support flexible execution:

```
pytest Execution Command
   │
   ├──> pytest tests/unit               (-m simulator / unit)
   ├──> pytest tests/integration        (-m integration)
   ├──> pytest tests/functional         (-m functional)
   ├──> pytest tests/regression         (-m regression)
   ├──> pytest tests/negative           (-m negative)
   └──> pytest tests/performance        (-m performance)
```

### 2. Fixture Lifecycle Architecture (`python/tests/conftest.py`)
To ensure total test isolation and zero socket leakage, fixture composition follows strict lifecycle boundaries:

$$\text{Simulator Fixture (start / yield / stop)} \longrightarrow \text{TCPTransport (connect)} \longrightarrow \text{Instrument Driver} \longrightarrow \text{Test Execution} \longrightarrow \text{Teardown (disconnect)}$$

* **`opm_sim` / `switch_sim` / `scope_sim` / `net_switch_sim`**: In-process TCP simulators bound to `127.0.0.1` on dynamic OS ports (`port=0`).
* **`opm_client` / `switch_client` / `scope_client` / `net_switch_client`**: Auto-connecting instrument driver clients.

### 3. Assertion & Telemetry Infrastructure (`python/tests/utilities/`)
* **Assertion Helpers (`assertions.py`)**: Domain-specific assertion wrappers (`assert_within_tolerance`, `assert_greater_than`, `assert_less_than`, `assert_in_range`) with explicit diagnostic error context.
* **Timing & Polling (`helpers.py`)**: High-resolution execution timing (`measure_execution_time`) and polling condition synchronization (`wait_until_condition`).
* **Telemetry Reporting (`reporting.py`)**: `TestMeasurementResult` records serialized to local `test_results.json` via `JSONResultExporter`.

---

## Milestone v0.3 Instrument & Simulator Subsystems

### 1. Layered Interface Composition Pattern
$$\text{Instrument / Device Driver} \longrightarrow \text{SCPI Protocol} \longrightarrow \text{BaseTransport} \longrightarrow \text{TCP Simulator (127.0.0.1)}$$

* `OpticalPowerMeter` $\rightarrow$ `SCPIProtocol` $\rightarrow$ `TCPTransport` $\rightarrow$ `OpticalPowerMeterSimulator`
* `OpticalSwitch` $\rightarrow$ `SCPIProtocol` $\rightarrow$ `TCPTransport` $\rightarrow$ `OpticalSwitchSimulator`
* `OpticalOscilloscope` $\rightarrow$ `SCPIProtocol` $\rightarrow$ `TCPTransport` $\rightarrow$ `OpticalOscilloscopeSimulator`
* `NetworkSwitch` $\rightarrow$ `SCPIProtocol` $\rightarrow$ `TCPTransport` $\rightarrow$ `NetworkSwitchSimulator`

### 2. Instrument Subsystem (`lablink.instruments` & `lablink.devices`)
* **`BaseInstrument`**: Abstract base class composing a `BaseTransport` and `SCPIProtocol`.
* **`OpticalPowerMeter`**: Software driver for optical power meters supporting wavelength tuning (`CONF:WAVELENGTH`), measurement units (`CONF:UNIT`), and power readings (`MEAS:POW?`).
* **`OpticalSwitch`**: Software driver for optical channel switch matrices (`ROUTE:SET`, `ROUTE?`, `ROUTE:CHAN:COUNT?`).
* **`OpticalOscilloscope`**: Software driver for optical oscilloscopes (`TIMEBASE:SCALE`, `CHANNEL:SCALE`, `ACQUIRE:STATE`, `WAVEFORM:DATA?`).
* **`NetworkSwitch`**: Device control abstraction for network switches (`enable_port`, `disable_port`, `get_port_state`, `get_all_port_states`).

---

## Implementation Status (Milestone v0.4)

### Implemented Functionality
* [x] Abstract transport interface contract (`BaseTransport`) & client transports (`TCPTransport`, `SerialTransport`, `MockTransport`)
* [x] SCPI protocol handler (`SCPIProtocol`) & IEEE 488.2 common commands (`*IDN?`, `*RST`, `*CLS`, `SYST:ERR?`)
* [x] VISA-style resource manager (`VISAResourceManager`) & resource wrapper (`VISAResource`)
* [x] Base instrument abstraction (`BaseInstrument`) & concrete instrument drivers (`OpticalPowerMeter`, `OpticalSwitch`, `OpticalOscilloscope`, `NetworkSwitch`)
* [x] In-process TCP SCPI software simulators (`OpticalPowerMeterSimulator`, `OpticalSwitchSimulator`, `OpticalOscilloscopeSimulator`, `NetworkSwitchSimulator`)
* [x] Pytest test automation framework structure (`conftest.py`, `functional/`, `regression/`, `negative/`, `performance/`, `utilities/`)
* [x] Pytest markers (`functional`, `regression`, `negative`, `performance`, `instrument`, `simulator`)
* [x] Custom measurement assertion helpers & JSON telemetry exporter (`test_results.json`)
* [x] Hardware-free unit, integration, functional, regression, negative, and performance test suites

### Deliberately Deferred Functionality (Future Milestones)
* [ ] Physical optical equipment validation (No physical optical hardware attached)
* [ ] NI-VISA native binary driver bindings — *Deferred*
* [ ] IXIA hardware integration — *Deferred*
* [ ] Layer-2 Ethernet raw frame testing, packet generation & traffic generator — *Milestone v0.5*
* [ ] PostgreSQL database persistence & schema migrations — *Milestone v0.5*
* [ ] ASP.NET Core test management REST API endpoints — *Milestone v0.5*
* [ ] Jenkins CI/CD pipelines & Docker environment orchestration — *Milestone v0.6*
