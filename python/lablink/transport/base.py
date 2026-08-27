"""
LabLink Base Transport Abstraction.

Defines the core interface contract for all communication transports
(TCP/IP, Serial RS-232, Mock Transports).
"""

from abc import ABC, abstractmethod

from lablink.exceptions import DisconnectedTransportError


class BaseTransport(ABC):
    """
    Abstract Base Class for all LabLink communication transports.

    Subclasses must implement connect(), disconnect(), write(), and read().
    """

    def __init__(self, timeout: float = 5.0) -> None:
        self._timeout: float = timeout
        self._is_connected: bool = False

    @property
    def is_connected(self) -> bool:
        """Return True if the transport connection is currently active."""
        return self._is_connected

    @property
    def timeout(self) -> float:
        """Return the current socket or serial operation timeout in seconds."""
        return self._timeout

    @timeout.setter
    def timeout(self, value: float) -> None:
        """Set the operation timeout in seconds."""
        if value < 0:
            raise ValueError("Timeout must be non-negative")
        self._timeout = value
        self._update_timeout(value)

    def _update_timeout(self, value: float) -> None:
        """Hook method for subclasses to apply timeout updates to native sockets/ports."""

    def _ensure_connected(self) -> None:
        """Helper method to raise DisconnectedTransportError if transport is offline."""
        if not self._is_connected:
            raise DisconnectedTransportError("Operation failed: transport is disconnected.")

    @abstractmethod
    def connect(self) -> None:
        """
        Establish transport connection.

        Raises:
            TransportConnectionError: If connection attempt fails.
            TransportTimeoutError: If connection attempt times out.
        """
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """Cleanly close and terminate transport connection."""
        ...

    @abstractmethod
    def write(self, data: bytes | str) -> int:
        """
        Write payload data to the transport stream.

        Args:
            data: Payload as bytes or string (strings will be encoded to UTF-8).

        Returns:
            Number of bytes written.

        Raises:
            DisconnectedTransportError: If transport is not connected.
            TransportTimeoutError: If write operation times out.
            TransportIOError: If an I/O stream error occurs.
        """
        ...

    @abstractmethod
    def read(self, size: int = 1024) -> bytes:
        """
        Read up to `size` bytes from the transport stream.

        Args:
            size: Maximum number of bytes to read.

        Returns:
            Bytes read from stream.

        Raises:
            DisconnectedTransportError: If transport is not connected.
            TransportTimeoutError: If read operation times out.
            TransportIOError: If stream error or unexpected EOF occurs.
        """
        ...

    def query(self, data: bytes | str, read_size: int = 1024) -> bytes:
        """
        Convenience method to perform a write followed immediately by a read.

        Args:
            data: Payload to send.
            read_size: Maximum bytes to receive.

        Returns:
            Response payload bytes.
        """
        self.write(data)
        return self.read(size=read_size)
