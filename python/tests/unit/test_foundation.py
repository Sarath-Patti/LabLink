"""
Foundational Infrastructure Tests.

Verifies package initialization, version metadata, configuration loading,
and logging system setup.
"""

import logging
import os

import lablink
from lablink.config import (
    DatabaseConfig,
    ExecutionConfig,
    InstrumentConfig,
    LabLinkConfig,
    SimulatorConfig,
    TransportConfig,
)
from lablink.logging import get_logger, setup_logging


def test_package_import_and_version() -> None:
    """Verify that the lablink package imports cleanly and exposes version 0.7.0."""
    assert lablink.__version__ == "0.7.0"
    assert hasattr(lablink, "__author__")


def test_default_configuration_loading() -> None:
    """Verify that default LabLinkConfig loads default sub-configurations."""
    config = LabLinkConfig.from_env()

    assert isinstance(config.transport, TransportConfig)
    assert isinstance(config.instruments, InstrumentConfig)
    assert isinstance(config.database, DatabaseConfig)
    assert isinstance(config.simulators, SimulatorConfig)
    assert isinstance(config.execution, ExecutionConfig)

    assert (
        config.transport.tcp_defaultTimeout_sec
        if hasattr(config.transport, "tcp_defaultTimeout_sec")
        else config.transport.tcp_default_timeout_sec == 5.0
    )
    assert config.instruments.scpi_timeout_ms == 5000
    assert config.database.host == "localhost"
    assert config.execution.environment == "development"


def test_configuration_secret_masking() -> None:
    """Verify that configuration dictionary export masks sensitive password fields."""
    os.environ["LABLINK_DB_PASSWORD"] = "super_secret_db_pass"
    try:
        config = LabLinkConfig.from_env()
        exported = config.to_dict(mask_secrets=True)

        assert exported["database"]["password"] == "***MASKED***"
        assert config.database.password == "super_secret_db_pass"
    finally:
        os.environ.pop("LABLINK_DB_PASSWORD", None)


def test_logging_system_initialization() -> None:
    """Verify that setup_logging initializes the root logger and get_logger returns child loggers."""
    logger = setup_logging(log_level="DEBUG")
    assert logger.name == "lablink"
    assert logger.level == logging.DEBUG

    child_logger = get_logger("transport.tcp")
    assert child_logger.name == "lablink.transport.tcp"
