# LabLink High-Level System Architecture

## Architecture Overview

LabLink is a multi-tier network and laboratory instrument test automation platform designed with strict separation of concerns across two primary technical stacks:

1. **Python Layer (`python/`)**
   * **Role:** Primary test automation engine, instrument integration, protocol parsing, hardware transport execution, Layer-2 Ethernet validation, software traffic generation, and pytest automation framework.
   * **Responsibility:** Executes SCPI commands, manages TCP/IP, RS-232 serial, and Layer-2 Ethernet streams, drives instrument drivers, software simulators, software traffic engines, and runs pytest automation workflows.

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

## Milestone v0.5 Layer-2 Ethernet & Network Validation Architecture

### 1. Layer-2 Subsystem Composition (`lablink.network`)
The Layer-2 network validation subsystem provides typed abstractions for Ethernet MAC framing, 802.1Q VLAN tagging, software traffic generation, and traffic sink sequence tracking:

$$\text{TrafficGenerator} \longrightarrow \text{EthernetFrame (MACAddress + VLANHeader)} \longrightarrow \text{TrafficSink} \longrightarrow \text{TrafficStatistics}$$

* **`MACAddress`**: Validated 48-bit MAC address value object supporting colon/hyphen/raw hex formats, byte serialization, and broadcast/multicast classification.
* **`VLANHeader`**: IEEE 802.1Q 4-byte VLAN tag model supporting VLAN IDs (`0..4095`), Priority Code Point (`0..7`), and DEI flags.
* **`EthernetFrame`**: Untagged and 802.1Q tagged MAC frame serialization and parsing with sequence number and nanosecond timestamp embedding.
* **`TrafficGenerator`**: Software traffic generator producing deterministic Ethernet frame streams with sequence tracking and payload padding.
* **`TrafficSink`**: Receiver and analyzer tracking sequence gaps, lost frames, duplicate frames, corrupted frames, and timestamp latencies.
* **`TrafficStatistics`**: Dataclass representing throughput (bytes/sec, bits/sec, frames/sec), packet loss percentages, and latency metrics.

---

## Milestone v0.4 Test Automation Framework Architecture

### 1. Test Layer Composition & Selective Execution Map
```
pytest Execution Command
   │
   ├──> pytest tests/unit               (-m simulator / unit)
   ├──> pytest tests/integration        (-m integration)
   ├──> pytest tests/functional         (-m functional)
   ├──> pytest tests/regression         (-m regression)
   ├──> pytest tests/negative           (-m negative)
   ├──> pytest tests/performance        (-m performance)
   └──> pytest -m l2                    (-m l2)
```

### 2. Fixture Lifecycle Architecture (`python/tests/conftest.py`)
$$\text{Simulator Fixture (start / yield / stop)} \longrightarrow \text{TCPTransport (connect)} \longrightarrow \text{Instrument Driver} \longrightarrow \text{Test Execution} \longrightarrow \text{Teardown (disconnect)}$$

---

## Milestone v0.3 Instrument & Simulator Subsystems

### 1. Layered Interface Composition Pattern
$$\text{Instrument / Device Driver} \longrightarrow \text{SCPI Protocol} \longrightarrow \text{BaseTransport} \longrightarrow \text{TCP Simulator (127.0.0.1)}$$

* `OpticalPowerMeter` $\rightarrow$ `SCPIProtocol` $\rightarrow$ `TCPTransport` $\rightarrow$ `OpticalPowerMeterSimulator`
* `OpticalSwitch` $\rightarrow$ `SCPIProtocol` $\rightarrow$ `TCPTransport` $\rightarrow$ `OpticalSwitchSimulator`
* `OpticalOscilloscope` $\rightarrow$ `SCPIProtocol` $\rightarrow$ `TCPTransport` $\rightarrow$ `OpticalOscilloscopeSimulator`
* `NetworkSwitch` $\rightarrow$ `SCPIProtocol` $\rightarrow$ `TCPTransport` $\rightarrow$ `NetworkSwitchSimulator`

---

## Implementation Status (Milestone v0.5)

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
* [x] Pytest test automation framework structure & markers (`l2`, `functional`, `regression`, `negative`, `performance`, `instrument`, `simulator`)
* [x] Custom measurement assertion helpers & JSON telemetry exporter (`test_results.json`)
* [x] Hardware-free unit, integration, functional, regression, negative, and performance test suites

### Deliberately Deferred Functionality (Future Milestones)
* [ ] Physical optical equipment validation (No physical optical hardware attached)
* [ ] NI-VISA native binary driver bindings — *Deferred*
* [ ] IXIA hardware integration — *Deferred*
* [ ] Kernel-bypass networking / DPDK drivers — *Deferred*
* [ ] PostgreSQL database persistence & schema migrations — *Milestone v0.6*
* [ ] ASP.NET Core test management REST API endpoints — *Milestone v0.6*
* [ ] Jenkins CI/CD pipelines & Docker environment orchestration — *Milestone v0.6*
