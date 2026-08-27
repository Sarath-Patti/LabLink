"""
LabLink TCP/IP Network Transport.

Provides client TCP socket communication for network-attached instruments,
simulators, and automated test endpoints.
"""

import socket

from lablink.exceptions import (
    TransportConnectionError,
    TransportIOError,
    TransportTimeoutError,
)
from lablink.logging import get_logger
from lablink.transport.base import BaseTransport

logger = get_logger("transport.tcp")


class TCPTransport(BaseTransport):
    """
    TCP/IP Socket Client Transport implementation.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 5025, timeout: float = 5.0) -> None:
        super().__init__(timeout=timeout)
        self.host: str = host
        self.port: int = port
        self._socket: socket.socket | None = None

    def _update_timeout(self, value: float) -> None:
        if self._socket:
            self._socket.settimeout(value)

    def connect(self) -> None:
        """Connect to the target TCP server host and port."""
        if self._is_connected:
            logger.debug(f"TCP transport already connected to {self.host}:{self.port}")
            return

        logger.info(
            f"Connecting TCP transport to {self.host}:{self.port} (timeout={self._timeout}s)..."
        )
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self._timeout)
            sock.connect((self.host, self.port))
            self._socket = sock
            self._is_connected = True
            logger.info(f"Successfully connected TCP transport to {self.host}:{self.port}")
        except TimeoutError as e:
            self._is_connected = False
            self._socket = None
            msg = (
                f"TCP connection attempt to {self.host}:{self.port} timed out after"
                f" {self._timeout}s"
            )
            logger.error(msg)
            raise TransportTimeoutError(msg) from e
        except OSError as e:
            self._is_connected = False
            self._socket = None
            msg = f"Failed to connect TCP transport to {self.host}:{self.port}: {e}"
            logger.error(msg)
            raise TransportConnectionError(msg) from e

    def disconnect(self) -> None:
        """Close TCP socket connection."""
        if not self._is_connected and self._socket is None:
            return

        logger.info(f"Disconnecting TCP transport from {self.host}:{self.port}...")
        if self._socket:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            finally:
                self._socket.close()
                self._socket = None
        self._is_connected = False
        logger.info(f"TCP transport disconnected from {self.host}:{self.port}")

    def write(self, data: bytes | str) -> int:
        """Write data to the connected TCP socket."""
        self._ensure_connected()
        assert self._socket is not None

        payload = data.encode("utf-8") if isinstance(data, str) else data
        try:
            self._socket.sendall(payload)
            logger.debug(f"TCP wrote {len(payload)} bytes to {self.host}:{self.port}")
            return len(payload)
        except TimeoutError as e:
            msg = f"TCP write to {self.host}:{self.port} timed out"
            logger.error(msg)
            raise TransportTimeoutError(msg) from e
        except OSError as e:
            self._is_connected = False
            msg = f"TCP write error to {self.host}:{self.port}: {e}"
            logger.error(msg)
            raise TransportIOError(msg) from e

    def read(self, size: int = 1024) -> bytes:
        """Read up to `size` bytes from the connected TCP socket."""
        self._ensure_connected()
        assert self._socket is not None

        try:
            data = self._socket.recv(size)
            if not data:
                self._is_connected = False
                msg = f"TCP connection closed by remote host {self.host}:{self.port}"
                logger.warning(msg)
                raise TransportIOError(msg)
            logger.debug(f"TCP read {len(data)} bytes from {self.host}:{self.port}")
            return data
        except TimeoutError as e:
            msg = f"TCP read from {self.host}:{self.port} timed out after {self._timeout}s"
            logger.warning(msg)
            raise TransportTimeoutError(msg) from e
        except OSError as e:
            self._is_connected = False
            msg = f"TCP read error from {self.host}:{self.port}: {e}"
            logger.error(msg)
            raise TransportIOError(msg) from e
