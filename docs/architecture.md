# LabLink High-Level System Architecture

## Architecture Overview

LabLink is a multi-tier network and laboratory instrument test automation platform designed with strict separation of concerns across two primary technical stacks:

1. **Python Layer (`python/`)**
   * **Role:** Primary test automation engine, instrument integration, protocol parsing, and hardware transport execution.
   * **Responsibility:** Executes SCPI commands, manages TCP/IP, RS-232 serial, and Layer-2 Ethernet streams, drives instrument drivers, and runs pytest automation workflows.

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

## Layer Separation & Extensions

* `lablink.config`: Unified, environment-aware configuration loader with secret masking.
* `lablink.logging`: Centralized logging with credential redaction.
* `lablink.transport`: Socket, serial, and ethernet communication primitives (Milestone v0.2).
* `lablink.protocols`: Protocol parsers including SCPI formatting (Milestone v0.2).
* `lablink.instruments`: Concrete instrument driver abstractions (Milestone v0.3).
* `lablink.devices`: Higher-level test target composite device abstractions (Milestone v0.3).
* `simulators`: Software-based virtual hardware targets for HIL testing (Milestone v0.3).
* `dotnet/LabLink.Api`: ASP.NET Core Web API service host (Milestones v0.1 - v0.5).
