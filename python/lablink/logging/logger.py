"""
LabLink Unified Logging System.

Provides consistent, structured, and sanitized logging across all LabLink modules.
Includes automatic credential redaction filters to prevent accidental disclosure
of passwords, secrets, and API tokens.
"""

import logging
import re
import sys
from typing import ClassVar, TextIO


class CredentialRedactingFormatter(logging.Formatter):
    """
    Custom logging Formatter that redacts passwords, tokens, and credentials
    from log output to maintain security hygiene.
    """

    PATTERNS: ClassVar[tuple[tuple[re.Pattern[str], str], ...]] = (
        (
            re.compile(r"(password['\"]?\s*[:=]\s*['\"]?)([^'\";\s]+)", re.IGNORECASE),
            r"\1***REDACTED***",
        ),
        (
            re.compile(r"(token['\"]?\s*[:=]\s*['\"]?)([^'\";\s]+)", re.IGNORECASE),
            r"\1***REDACTED***",
        ),
        (
            re.compile(r"(secret['\"]?\s*[:=]\s*['\"]?)([^'\";\s]+)", re.IGNORECASE),
            r"\1***REDACTED***",
        ),
        (
            re.compile(r"(api_key['\"]?\s*[:=]\s*['\"]?)([^'\";\s]+)", re.IGNORECASE),
            r"\1***REDACTED***",
        ),
    )

    def format(self, record: logging.LogRecord) -> str:
        formatted = super().format(record)
        for pattern, replacement in self.PATTERNS:
            formatted = pattern.sub(replacement, formatted)
        return formatted


DEFAULT_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    log_level: str = "INFO",
    log_format: str | None = None,
    date_format: str | None = None,
    stream: TextIO | None = None,
) -> logging.Logger:
    """
    Configure the root logger for the LabLink application.

    Args:
        log_level: Desired log level string ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_format: Custom log line format string
        date_format: Custom timestamp format string
        stream: Target text stream for log output (defaults to sys.stdout)

    Returns:
        The configured 'lablink' parent logger instance.
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logger = logging.getLogger("lablink")
    logger.setLevel(numeric_level)

    # Avoid duplicate handlers if setup_logging is called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    handler = logging.StreamHandler(stream or sys.stdout)
    handler.setLevel(numeric_level)

    formatter = CredentialRedactingFormatter(
        fmt=log_format or DEFAULT_LOG_FORMAT,
        datefmt=date_format or DEFAULT_DATE_FORMAT,
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtain a child logger under the 'lablink' root namespace.

    Example:
        >>> logger = get_logger("transport.tcp")
        >>> logger.name
        'lablink.transport.tcp'
    """
    if name.startswith("lablink."):
        return logging.getLogger(name)
    return logging.getLogger(f"lablink.{name}")
