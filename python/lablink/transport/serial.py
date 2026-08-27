"""
LabLink RS-232 / Serial Transport Abstraction.

Provides serial communication support for legacy instruments and serial interfaces.
Supports backend abstraction allowing unit testing without physical RS-232 hardware.
"""

from typing import Any, Protocol

from lablink.exceptions import (
    TransportConnectionError,
    TransportIOError,
    TransportTimeoutError,
)
from lablink.logging import get_logger
from lablink.transport.base import BaseTransport

logger = get_logger("transport.serial")


class SerialPortBackend(Protocol):
    """Protocol interface for underlying serial port implementations."""

    is_open: bool

    def open(self) -> None: ...

    def close(self) -> None: ...

    def write(self, data: bytes) -> int: ...

    def read(self, size: int) -> bytes: ...


class SerialTransport(BaseTransport):
    """
    RS-232 Serial Transport implementation.

    Delegates hardware serial I/O to a serial backend port instance or optional
    mock port backend for hardware-free unit testing.
    """

    def __init__(
        self,
        port: str = "COM1",
        baudrate: int = 9600,
        bytesize: int = 8,
        parity: str = "N",
        stopbits: float = 1.0,
        timeout: float = 2.0,
        backend: Any | None = None,
    ) -> None:
        super().__init__(timeout=timeout)
        self.port: str = port
        self.baudrate: int = baudrate
        self.bytesize: int = bytesize
        self.parity: str = parity
        self.stopbits: float = stopbits
        self._backend: Any | None = backend

    def connect(self) -> None:
        """Establish serial port connection."""
        if self._is_connected:
            return

        logger.info(f"Opening Serial port {self.port} at {self.baudrate} baud...")
        try:
            if self._backend is None:
                # Attempt importing pyserial dynamically if available
                try:
                    import serial  # type: ignore

                    self._backend = serial.Serial(
                        port=self.port,
                        baudrate=self.baudrate,
                        bytesize=self.bytesize,
                        parity=self.parity,
                        stopbits=self.stopbits,
                        timeout=self._timeout,
                    )
                except ImportError:
                    # Provide virtual serial interface fallback when pyserial is unavailable
                    logger.debug("pyserial module not found; using virtual serial backend handler.")
                    self._backend = _VirtualSerialBackend(self.port, self.baudrate, self._timeout)
                    self._backend.open()
            else:
                if hasattr(self._backend, "open") and not getattr(self._backend, "is_open", False):
                    self._backend.open()

            self._is_connected = True
            logger.info(f"Serial port {self.port} opened successfully.")
        except Exception as e:
            self._is_connected = False
            msg = f"Failed to open serial port {self.port}: {e}"
            logger.error(msg)
            raise TransportConnectionError(msg) from e

    def disconnect(self) -> None:
        """Close serial port connection."""
        if not self._is_connected:
            return

        logger.info(f"Closing Serial port {self.port}...")
        if self._backend and hasattr(self._backend, "close"):
            try:
                self._backend.close()
            except (OSError, AttributeError, RuntimeError) as e:
                logger.warning(f"Error closing serial port {self.port}: {e}")
        self._is_connected = False
        logger.info(f"Serial port {self.port} closed.")

    def write(self, data: bytes | str) -> int:
        """Write payload bytes or string to serial port."""
        self._ensure_connected()
        assert self._backend is not None

        payload = data.encode("utf-8") if isinstance(data, str) else data
        try:
            bytes_written = self._backend.write(payload)
            logger.debug(f"Serial wrote {bytes_written} bytes to {self.port}")
            return bytes_written or len(payload)
        except TimeoutError as e:
            raise TransportTimeoutError(f"Serial write timeout on {self.port}") from e
        except Exception as e:
            raise TransportIOError(f"Serial write failed on {self.port}: {e}") from e

    def read(self, size: int = 1024) -> bytes:
        """Read up to `size` bytes from serial port."""
        self._ensure_connected()
        assert self._backend is not None

        try:
            raw_data = self._backend.read(size)
            data: bytes = raw_data if isinstance(raw_data, bytes) else bytes(raw_data or b"")
            logger.debug(f"Serial read {len(data)} bytes from {self.port}")
            return data
        except TimeoutError as e:
            raise TransportTimeoutError(f"Serial read timeout on {self.port}") from e
        except Exception as e:
            raise TransportIOError(f"Serial read failed on {self.port}: {e}") from e


class _VirtualSerialBackend:
    """In-memory virtual serial backend fallback for non-hardware environments."""

    def __init__(self, port: str, baudrate: int, timeout: float) -> None:
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.is_open = False
        self._rx_buffer = bytearray()

    def open(self) -> None:
        self.is_open = True

    def close(self) -> None:
        self.is_open = False

    def write(self, data: bytes) -> int:
        if not self.is_open:
            raise RuntimeError("Serial port is closed")
        return len(data)

    def read(self, size: int) -> bytes:
        if not self.is_open:
            raise RuntimeError("Serial port is closed")
        chunk = bytes(self._rx_buffer[:size])
        del self._rx_buffer[:size]
        return chunk
