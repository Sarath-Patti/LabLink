"""
LabLink Configuration Management System.

Provides environment-aware, modular configuration settings for LabLink
transport layers, protocols, instruments, databases, and test execution.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TransportConfig:
    """Configuration for physical and network transport protocols."""

    tcp_default_host: str = field(
        default_factory=lambda: os.getenv("LABLINK_TCP_HOST", "127.0.0.1")
    )
    tcp_default_port: int = field(
        default_factory=lambda: int(os.getenv("LABLINK_TCP_PORT", "5025"))
    )
    tcp_default_timeout_sec: float = field(
        default_factory=lambda: float(os.getenv("LABLINK_TCP_TIMEOUT", "5.0"))
    )
    tcp_connect_retry_attempts: int = 3

    serial_default_port: str = field(
        default_factory=lambda: os.getenv("LABLINK_SERIAL_PORT", "COM1")
    )
    serial_default_baudrate: int = field(
        default_factory=lambda: int(os.getenv("LABLINK_SERIAL_BAUDRATE", "9600"))
    )
    serial_default_bytesize: int = field(
        default_factory=lambda: int(os.getenv("LABLINK_SERIAL_BYTESIZE", "8"))
    )
    serial_default_parity: str = field(
        default_factory=lambda: os.getenv("LABLINK_SERIAL_PARITY", "N")
    )
    serial_default_stopbits: float = field(
        default_factory=lambda: float(os.getenv("LABLINK_SERIAL_STOPBITS", "1.0"))
    )
    serial_default_timeout_sec: float = field(
        default_factory=lambda: float(os.getenv("LABLINK_SERIAL_TIMEOUT", "2.0"))
    )

    ethernet_interface: str = field(
        default_factory=lambda: os.getenv("LABLINK_ETH_INTERFACE", "eth0")
    )


@dataclass
class InstrumentConfig:
    """Configuration for instrument communication and SCPI settings."""

    scpi_default_read_termination: str = "\n"
    scpi_default_write_termination: str = "\n"
    scpi_timeout_ms: int = field(
        default_factory=lambda: int(os.getenv("LABLINK_SCPI_TIMEOUT_MS", "5000"))
    )
    instrument_retry_count: int = 2


@dataclass
class DatabaseConfig:
    """Configuration for PostgreSQL database persistence."""

    host: str = field(default_factory=lambda: os.getenv("LABLINK_DB_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("LABLINK_DB_PORT", "5432")))
    name: str = field(default_factory=lambda: os.getenv("LABLINK_DB_NAME", "lablink_db"))
    user: str = field(default_factory=lambda: os.getenv("LABLINK_DB_USER", "lablink_user"))
    # Secrets are strictly populated from environment variables
    password: str = field(default_factory=lambda: os.getenv("LABLINK_DB_PASSWORD", ""))
    max_connections: int = field(
        default_factory=lambda: int(os.getenv("LABLINK_DB_MAX_CONN", "10"))
    )


@dataclass
class SimulatorConfig:
    """Configuration for instrument software simulators."""

    enabled: bool = field(
        default_factory=lambda: os.getenv("LABLINK_SIMULATORS_ENABLED", "false").lower() == "true"
    )
    tcp_simulator_port: int = field(
        default_factory=lambda: int(os.getenv("LABLINK_SIM_TCP_PORT", "9001"))
    )
    scpi_sim_response_delay_ms: float = 10.0


@dataclass
class ExecutionConfig:
    """Configuration for test execution environments."""

    environment: str = field(default_factory=lambda: os.getenv("LABLINK_ENV", "development"))
    log_level: str = field(default_factory=lambda: os.getenv("LABLINK_LOG_LEVEL", "INFO"))
    max_parallel_tests: int = field(
        default_factory=lambda: int(os.getenv("LABLINK_PARALLEL_TESTS", "1"))
    )


class LabLinkConfig:
    """
    Main configuration aggregator for LabLink modules.

    Supports loading defaults, environment variable overrides,
    and optional JSON configuration file loading.
    """

    def __init__(
        self,
        transport: TransportConfig | None = None,
        instruments: InstrumentConfig | None = None,
        database: DatabaseConfig | None = None,
        simulators: SimulatorConfig | None = None,
        execution: ExecutionConfig | None = None,
    ) -> None:
        self.transport = transport or TransportConfig()
        self.instruments = instruments or InstrumentConfig()
        self.database = database or DatabaseConfig()
        self.simulators = simulators or SimulatorConfig()
        self.execution = execution or ExecutionConfig()

    @classmethod
    def from_env(cls) -> "LabLinkConfig":
        """Construct configuration instance populated from environment variables."""
        return cls()

    @classmethod
    def from_file(cls, config_path: Path | str) -> "LabLinkConfig":
        """Load configuration from a JSON file with environment fallbacks."""
        path = Path(config_path)
        if not path.is_file():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LabLinkConfig":
        """Construct configuration instance from a dictionary."""
        transport_data = data.get("transport", {})
        instrument_data = data.get("instruments", {})
        database_data = data.get("database", {})
        simulator_data = data.get("simulators", {})
        execution_data = data.get("execution", {})

        return cls(
            transport=(TransportConfig(**transport_data) if transport_data else TransportConfig()),
            instruments=(
                InstrumentConfig(**instrument_data) if instrument_data else InstrumentConfig()
            ),
            database=(DatabaseConfig(**database_data) if database_data else DatabaseConfig()),
            simulators=(SimulatorConfig(**simulator_data) if simulator_data else SimulatorConfig()),
            execution=(ExecutionConfig(**execution_data) if execution_data else ExecutionConfig()),
        )

    def to_dict(self, mask_secrets: bool = True) -> dict[str, Any]:
        """Convert current configuration to a dictionary, optionally masking secrets."""
        db_dict = {
            "host": self.database.host,
            "port": self.database.port,
            "name": self.database.name,
            "user": self.database.user,
            "password": (
                "***MASKED***"
                if mask_secrets and self.database.password
                else self.database.password
            ),
            "max_connections": self.database.max_connections,
        }

        return {
            "transport": {
                "tcp_default_host": self.transport.tcp_default_host,
                "tcp_default_port": self.transport.tcp_default_port,
                "tcp_default_timeout_sec": self.transport.tcp_default_timeout_sec,
                "tcp_connect_retry_attempts": self.transport.tcp_connect_retry_attempts,
                "serial_default_port": self.transport.serial_default_port,
                "serial_default_baudrate": self.transport.serial_default_baudrate,
                "serial_default_bytesize": self.transport.serial_default_bytesize,
                "serial_default_parity": self.transport.serial_default_parity,
                "serial_default_stopbits": self.transport.serial_default_stopbits,
                "serial_default_timeout_sec": self.transport.serial_default_timeout_sec,
                "ethernet_interface": self.transport.ethernet_interface,
            },
            "instruments": {
                "scpi_default_read_termination": repr(
                    self.instruments.scpi_default_read_termination
                ),
                "scpi_default_write_termination": repr(
                    self.instruments.scpi_default_write_termination
                ),
                "scpi_timeout_ms": self.instruments.scpi_timeout_ms,
                "instrument_retry_count": self.instruments.instrument_retry_count,
            },
            "database": db_dict,
            "simulators": {
                "enabled": self.simulators.enabled,
                "tcp_simulator_port": self.simulators.tcp_simulator_port,
                "scpi_sim_response_delay_ms": self.simulators.scpi_sim_response_delay_ms,
            },
            "execution": {
                "environment": self.execution.environment,
                "log_level": self.execution.log_level,
                "max_parallel_tests": self.execution.max_parallel_tests,
            },
        }
