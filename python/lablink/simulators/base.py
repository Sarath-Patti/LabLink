"""
LabLink Base Instrument Simulator Infrastructure.

Provides a thread-safe, in-process TCP SCPI instrument server listening on 127.0.0.1.
Supports automatic SCPI command parsing, FIFO error queue management, client handling,
and clean lifecycle shutdown.
"""

import socketserver
import threading
import time
from collections import deque

from lablink.logging import get_logger

logger = get_logger("simulators.base")


class _ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


class BaseInstrumentSimulator:
    """
    Abstract base software instrument simulator exposing a local TCP SCPI server.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 0,
        vendor: str = "LabLink",
        model: str = "SimulatedInstrument",
        serial_number: str = "SN0000",
        firmware_version: str = "v1.0",
    ) -> None:
        self.host: str = host
        self.requested_port: int = port
        self.vendor: str = vendor
        self.model: str = model
        self.serial_number: str = serial_number
        self.firmware_version: str = firmware_version

        self._error_queue: deque[tuple[int, str]] = deque()
        self._lock = threading.Lock()
        self._server: _ThreadedTCPServer | None = None
        self._server_thread: threading.Thread | None = None
        self._is_running: bool = False

    @property
    def is_running(self) -> bool:
        """Return True if simulator TCP server is active."""
        return self._is_running

    @property
    def server_address(self) -> tuple[str, int]:
        """Return bound (host, port) tuple of active TCP server."""
        if self._server:
            host_val, port_val = self._server.server_address[:2]
            return (str(host_val), int(port_val))
        return (self.host, self.requested_port)

    @property
    def port(self) -> int:
        """Return bound TCP port integer."""
        return self.server_address[1]

    def push_error(self, code: int, message: str) -> None:
        """Push SCPI error code and message into FIFO queue."""
        with self._lock:
            self._error_queue.append((code, message))

    def pop_error(self) -> tuple[int, str]:
        """Pop oldest SCPI error from FIFO queue (returns (0, 'No error') if empty)."""
        with self._lock:
            if self._error_queue:
                return self._error_queue.popleft()
            return (0, "No error")

    def clear_errors(self) -> None:
        """Clear all pending errors in FIFO queue."""
        with self._lock:
            self._error_queue.clear()

    def reset_state(self) -> None:
        """Reset simulator state to default values. Subclasses override to reset fields."""
        self.clear_errors()

    def start(self) -> None:
        """Start TCP server in background daemon thread."""
        if self._is_running:
            return

        logger.info(f"Starting {self.model} simulator on {self.host}:{self.requested_port}...")
        simulator_instance = self

        class Handler(socketserver.BaseRequestHandler):
            def handle(self) -> None:
                while simulator_instance.is_running:
                    try:
                        data = self.request.recv(1024)
                        if not data:
                            break
                        commands = data.decode("utf-8", errors="replace").strip().split("\n")
                        for command_str in commands:
                            cmd = command_str.strip()
                            if not cmd:
                                continue
                            response = simulator_instance._dispatch_command(cmd)
                            if response is not None:
                                self.request.sendall(response.encode("utf-8"))
                    except (ConnectionResetError, BrokenPipeError, OSError):
                        break

        self._server = _ThreadedTCPServer((self.host, self.requested_port), Handler)
        self._server_thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._server_thread.start()
        self._is_running = True
        time.sleep(0.05)  # Allow socket binding to complete
        logger.info(f"{self.model} simulator started on {self.server_address}.")

    def stop(self) -> None:
        """Shutdown TCP server and join background thread."""
        if not self._is_running:
            return

        logger.info(f"Stopping {self.model} simulator on {self.server_address}...")
        self._is_running = False
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
        if self._server_thread:
            self._server_thread.join(timeout=2.0)
            self._server_thread = None
        logger.info(f"{self.model} simulator stopped.")

    def _dispatch_command(self, cmd: str) -> str | None:
        """Dispatch received SCPI command to standard or subclass handler."""
        logger.debug(f"Simulator received SCPI command: {cmd!r}")
        cmd_upper = cmd.upper()

        if cmd_upper == "*IDN?":
            return f"{self.vendor},{self.model},{self.serial_number},{self.firmware_version}\n"
        if cmd_upper == "*RST":
            self.reset_state()
            return None
        if cmd_upper == "*CLS":
            self.clear_errors()
            return None
        if cmd_upper == "SYST:ERR?":
            code, msg = self.pop_error()
            sign = "+" if code >= 0 else ""
            return f'{sign}{code},"{msg}"\n'

        return self._handle_custom_command(cmd)

    def _handle_custom_command(self, cmd: str) -> str | None:
        """Subclass hook to handle instrument-specific SCPI commands."""
        self.push_error(-113, "Undefined header")
        return None
