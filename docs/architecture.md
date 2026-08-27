# LabLink High-Level System Architecture

## Architecture Overview

LabLink is a multi-tier network and laboratory instrument test automation platform designed with strict separation of concerns across two primary technical stacks:

1. **Python Layer (`python/`)**
   * **Role:** Primary test automation engine, instrument integration, protocol parsing, and hardware transport execution.
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

## Milestone v0.3 Instrument & Simulator Architecture

### 1. Layered Interface Composition Pattern
To prevent tight coupling between instruments, protocol messaging, and physical network layers, LabLink enforces strict object composition:

$$\text{Instrument / Device Driver} \longrightarrow \text{SCPI Protocol} \longrightarrow \text{BaseTransport} \longrightarrow \text{TCP Simulator (127.0.0.1)}$$

For example:
* `OpticalPowerMeter` $\rightarrow$ `SCPIProtocol` $\rightarrow$ `TCPTransport` $\rightarrow$ `OpticalPowerMeterSimulator`
* `OpticalSwitch` $\rightarrow$ `SCPIProtocol` $\rightarrow$ `TCPTransport` $\rightarrow$ `OpticalSwitchSimulator`
* `OpticalOscilloscope` $\rightarrow$ `SCPIProtocol` $\rightarrow$ `TCPTransport` $\rightarrow$ `OpticalOscilloscopeSimulator`
* `NetworkSwitch` $\rightarrow$ `SCPIProtocol` $\rightarrow$ `TCPTransport` $\rightarrow$ `NetworkSwitchSimulator`

### 2. Instrument Subsystem (`lablink.instruments` & `lablink.devices`)
* **`BaseInstrument`**: Abstract base class composing a `BaseTransport` and `SCPIProtocol`. Manages lifecycle (`connect`, `disconnect`), delegation (`write`, `read`, `query`), identification (`*IDN?`), reset (`*RST`), status clearing (`*CLS`), and SCPI error checks (`SYST:ERR?`).
* **`OpticalPowerMeter`**: Software driver for optical power meters supporting wavelength tuning (`CONF:WAVELENGTH`), measurement units (`CONF:UNIT`), and power readings (`MEAS:POW?`).
* **`OpticalSwitch`**: Software driver for optical channel switch matrices supporting channel selection (`ROUTE:SET`), active route queries (`ROUTE?`), and port capacity checks (`ROUTE:CHAN:COUNT?`).
* **`OpticalOscilloscope`**: Software driver for optical oscilloscopes supporting timebase scale (`TIMEBASE:SCALE`), channel scale (`CHANNEL:SCALE`), acquisition control (`ACQUIRE:STATE`), and structured `WaveformData` retrieval (`WAVEFORM:DATA?`).
* **`NetworkSwitch`**: Device control abstraction for network switches supporting port state configuration (`enable_port`, `disable_port`, `get_port_state`, `get_all_port_states`).

### 3. Software Simulators Subsystem (`lablink.simulators`)
* **`BaseInstrumentSimulator`**: Multithreaded TCP SCPI server listening on `127.0.0.1`. Features a thread-safe FIFO SCPI error queue (`SYST:ERR?`), standard command dispatches (`*IDN?`, `*RST`, `*CLS`), and clean lifecycle shutdown.
* **`OpticalPowerMeterSimulator`**: Deterministic SCPI server simulating power readings, wavelength configuration, and optional measurement noise.
* **`OpticalSwitchSimulator`**: SCPI server simulating channel switching, route verification, and out-of-range channel error handling.
* **`OpticalOscilloscopeSimulator`**: SCPI server generating deterministic waveform sample data scaled by timebase and channel settings.
* **`NetworkSwitchSimulator`**: SCPI server managing simulated port state tables.

### 4. Transport & Protocol Subsystems (`lablink.transport` & `lablink.protocols`)
* **`BaseTransport`**: Abstract base class defining uniform transport operations (`connect()`, `disconnect()`, `write()`, `read()`, `query()`) and state management (`is_connected`, `timeout`).
* **`TCPTransport`**: Client socket implementation for network-attached SCPI devices, test targets, and hardware simulators.
* **`SerialTransport`**: RS-232 serial stream transport supporting configurable baudrates and virtual backend fallback.
* **`MockTransport`**: In-memory transport for unit testing without network sockets.
* **`SCPIProtocol`**: Wraps any `BaseTransport` instance, handles command termination (`\n`, `\r\n`), implements IEEE 488.2 common commands (`*IDN?`, `*RST`, `*CLS`, `SYST:ERR?`), and provides numeric/boolean/error response parsing helpers.
* **`VISAResourceManager` & `VISAResource`**: Conceptual VISA-style resource interface parsing descriptors (`TCPIP0::...`, `ASRL1::...`, `MOCK::...`) without requiring external NI-VISA C-libraries or binary drivers.

---

## Implementation Status (Milestone v0.3)

### Implemented Functionality
* [x] Abstract transport interface contract (`BaseTransport`) & client transports (`TCPTransport`, `SerialTransport`, `MockTransport`)
* [x] SCPI protocol handler (`SCPIProtocol`) & IEEE 488.2 common commands (`*IDN?`, `*RST`, `*CLS`, `SYST:ERR?`)
* [x] VISA-style resource manager (`VISAResourceManager`) & resource wrapper (`VISAResource`)
* [x] Base instrument abstraction (`BaseInstrument`)
* [x] Optical Power Meter driver (`OpticalPowerMeter`) & TCP SCPI simulator (`OpticalPowerMeterSimulator`)
* [x] Optical Switch driver (`OpticalSwitch`) & TCP SCPI simulator (`OpticalSwitchSimulator`)
* [x] Optical Oscilloscope driver (`OpticalOscilloscope`) & TCP SCPI simulator (`OpticalOscilloscopeSimulator`)
* [x] Network Switch device control driver (`NetworkSwitch`) & TCP SCPI simulator (`NetworkSwitchSimulator`)
* [x] Base simulator TCP server (`BaseInstrumentSimulator`) with FIFO SCPI error queue
* [x] Hardware-free unit test suite (`tests/unit/`) & end-to-end local TCP integration tests (`tests/integration/`)

### Deliberately Deferred Functionality (Future Milestones)
* [ ] Physical optical equipment validation (No physical optical hardware attached)
* [ ] NI-VISA native binary driver bindings — *Deferred*
* [ ] IXIA hardware integration — *Deferred*
* [ ] Layer-2 Ethernet raw frame testing, packet generation & traffic generator — *Milestone v0.5*
* [ ] PostgreSQL database persistence & test log schema — *Milestone v0.4*
* [ ] ASP.NET Core test management REST API endpoints — *Milestone v0.5*
* [ ] Jenkins CI/CD pipelines & Docker environment orchestration — *Milestone v0.6*
