"""
LabLink Mock Transport for Hardware-Free Automated Testing.

Implements the BaseTransport contract using an in-memory buffer and response queue.
Allows unit tests to simulate network latency, timeouts, connection failures,
and custom response sequences.
"""

from collections.abc import Callable

from lablink.exceptions import (
    TransportConnectionError,
    TransportIOError,
    TransportTimeoutError,
)
from lablink.logging import get_logger
from lablink.transport.base import BaseTransport

logger = get_logger("transport.mock")


class MockTransport(BaseTransport):
    """
    In-memory Mock Transport for testing instrument drivers and protocol parsers.
    """

    def __init__(self, timeout: float = 1.0, auto_connect: bool = False) -> None:
        super().__init__(timeout=timeout)
        self.fail_connect: bool = False
        self.fail_read_timeout: bool = False
        self.fail_write_timeout: bool = False
        self.fail_io_error: bool = False

        self.written_history: list[bytes] = []
        self._read_queue: list[bytes] = []
        self._response_map: dict[bytes, bytes] = {}
        self._custom_handler: Callable[[bytes], bytes] | None = None

        if auto_connect:
            self._is_connected = True

    def add_response(self, request: bytes | str, response: bytes | str) -> None:
        """Register a deterministic request -> response payload mapping."""
        req_bytes = request.encode("utf-8") if isinstance(request, str) else request
        resp_bytes = response.encode("utf-8") if isinstance(response, str) else response
        self._response_map[req_bytes] = resp_bytes

    def push_read_data(self, data: bytes | str) -> None:
        """Push raw response data directly onto the read queue."""
        payload = data.encode("utf-8") if isinstance(data, str) else data
        self._read_queue.append(payload)

    def set_custom_handler(self, handler: Callable[[bytes], bytes]) -> None:
        """Set a dynamic callback handler for generating responses from requests."""
        self._custom_handler = handler

    def clear(self) -> None:
        """Clear written history, response queues, and failure triggers."""
        self.written_history.clear()
        self._read_queue.clear()
        self._response_map.clear()
        self._custom_handler = None
        self.fail_connect = False
        self.fail_read_timeout = False
        self.fail_write_timeout = False
        self.fail_io_error = False

    def connect(self) -> None:
        """Simulate connecting transport."""
        if self.fail_connect:
            self._is_connected = False
            logger.error("Mock transport simulated connection failure.")
            raise TransportConnectionError("Simulated connection failure")

        self._is_connected = True
        logger.info("Mock transport connected successfully.")

    def disconnect(self) -> None:
        """Simulate disconnecting transport."""
        self._is_connected = False
        logger.info("Mock transport disconnected.")

    def write(self, data: bytes | str) -> int:
        """Record written payload and lookup/enqueue response if configured."""
        self._ensure_connected()

        if self.fail_write_timeout:
            raise TransportTimeoutError("Simulated write timeout")
        if self.fail_io_error:
            raise TransportIOError("Simulated write I/O error")

        payload = data.encode("utf-8") if isinstance(data, str) else data
        self.written_history.append(payload)
        logger.debug(f"MockTransport wrote: {payload!r}")

        # Check response map
        if payload in self._response_map:
            self._read_queue.append(self._response_map[payload])
        elif self._custom_handler:
            resp = self._custom_handler(payload)
            self._read_queue.append(resp)

        return len(payload)

    def read(self, size: int = 1024) -> bytes:
        """Read queued response data from memory."""
        self._ensure_connected()

        if self.fail_read_timeout:
            raise TransportTimeoutError("Simulated read timeout")
        if self.fail_io_error:
            raise TransportIOError("Simulated read I/O error")

        if not self._read_queue:
            logger.warning("MockTransport read queue empty; returning b''")
            return b""

        data = self._read_queue.pop(0)
        chunk = data[:size]
        if len(data) > size:
            # Re-enqueue remaining unread chunk
            self._read_queue.insert(0, data[size:])

        logger.debug(f"MockTransport read: {chunk!r}")
        return chunk
