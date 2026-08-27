# LabLink: Network & Instrument Test Automation Platform

LabLink is an extensible, multi-tier network and laboratory instrument test automation platform. It provides Python-based instrument control and automated test execution alongside a C#/.NET service layer for test management.

---

## Architecture Overview

LabLink employs a decoupled multi-tiered architecture:

* **Python Layer (`python/`):** Primary engine for test automation, physical/network transport handling, SCPI protocol parsing, and hardware device control.
* **C# / .NET Layer (`dotnet/LabLink.Api`):** Service layer providing an ASP.NET Core Web API foundation for test management, run orchestration, and reporting.
* **Persistence Layer (Planned):** PostgreSQL database integration for historical test logs, device telemetry, and run results.
* **Infrastructure (Planned):** Docker-based integration environments and Jenkins CI/CD automation pipelines.

---

## Technology Stack

* **Automation & Drivers:** Python 3.10+
* **Test Framework:** pytest
* **Service API:** C# / .NET 8.0 ASP.NET Core
* **Persistence (Planned):** PostgreSQL
* **CI/CD & Containers (Planned):** Docker, Jenkins

---

## Repository Structure

```
LabLink/
├── python/
│   ├── lablink/
│   │   ├── config/          # Configuration loading & settings
│   │   ├── logging/         # Credential-redacting logging framework
│   │   ├── instruments/     # Instrument driver extension points
│   │   ├── transport/       # Transport layer extension points
│   │   ├── protocols/       # SCPI and protocol extension points
│   │   └── devices/         # Device abstraction extension points
│   ├── tests/
│   │   ├── unit/            # Unit test suite
│   │   └── integration/     # Integration test suite
│   └── pyproject.toml       # Python package configuration & dependencies
│
├── dotnet/
│   └── LabLink.Api/         # ASP.NET Core Web API foundation
│
├── config/                  # Safe configuration templates (.json, .env)
├── docs/                    # Architectural & design documentation
├── scripts/                 # Development lifecycle scripts (setup, test, clean)
├── simulators/              # Instrument simulators (Milestone v0.3)
├── ethernet/                # Layer-2 Ethernet test components (Milestone v0.2)
├── docker/                  # Docker containerization (Milestone v0.6)
├── jenkins/                 # Jenkins CI/CD pipelines (Milestone v0.6)
└── README.md
```

---

## Current Milestone Status

**Current Milestone:** `v0.1: Repository Foundation & Core Infrastructure`

### Implemented Functionality (Milestone v0.1)
* [x] Foundational repository structure & Git hygiene (`.gitignore`)
* [x] Python package structure & `pyproject.toml` configuration
* [x] Modular configuration management system (`lablink.config`) with secret masking
* [x] Centralized logging framework (`lablink.logging`) with credential redaction
* [x] Pytest infrastructure & foundational package import/configuration unit tests
* [x] Minimal ASP.NET Core 8 Web API foundation (`LabLink.Api`) with health endpoint (`/api/v1/health`)
* [x] Development helper scripts (`scripts/setup.sh`, `scripts/run_tests.sh`, `scripts/clean.sh`)
* [x] Architecture documentation (`docs/architecture.md`)

### Planned Functionality (Upcoming Milestones)
* [ ] **Milestone v0.2:** TCP/IP socket, RS-232 serial, SCPI protocol parser, and Layer-2 Ethernet transport drivers
* [ ] **Milestone v0.3:** Hardware instrument abstractions & virtual software simulators
* [ ] **Milestone v0.4:** PostgreSQL database migration schema & persistence layer
* [ ] **Milestone v0.5:** ASP.NET Core test-management REST API endpoints
* [ ] **Milestone v0.6:** Docker containerization & Jenkins CI/CD automation

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

Run tests using the project test script or directly via `pytest`:

```bash
# Option 1: Using the provided script
./scripts/run_tests.sh

# Option 2: Running pytest directly within the python directory
cd python
pytest
```

The current foundational tests verify package initialization, version metadata, configuration loading, secret masking, and logging behavior.

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
4. Access the health status endpoint at `http://localhost:5000/api/v1/health` (or configured port).

---

## Maintenance & Cleanup

To remove temporary build output, Python byte-code caches, and .NET compilation artifacts:

```bash
./scripts/clean.sh
```
