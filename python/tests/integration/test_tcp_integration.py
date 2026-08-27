"""
Local End-to-End Integration Test for TCPTransport and SCPIProtocol.

Uses an in-process TCP server running on localhost (127.0.0.1) with dynamic port
assignment to test real network socket communication without external network or hardware.
"""

import socketserver
import threading
import time

import pytest

from lablink.protocols.scpi import SCPIProtocol
from lablink.transport.tcp import TCPTransport


class MockSCPITCPServerHandler(socketserver.BaseRequestHandler):
    """Simple in-process SCPI command echo and handler for TCP integration testing."""

    def handle(self) -> None:
        while True:
            try:
                data = self.request.recv(1024)
                if not data:
                    break
                cmd = data.decode("utf-8").strip()

                if cmd == "*IDN?":
                    self.request.sendall(b"LabLink,MockServer,SN9999,v1.0\n")
                elif cmd == "*RST":
                    self.request.sendall(b"OK\n")
                elif cmd == "SYST:ERR?":
                    self.request.sendall(b'+0,"No error"\n')
                else:
                    self.request.sendall(f"ECHO:{cmd}\n".encode())
            except (ConnectionResetError, BrokenPipeError):
                break


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


@pytest.fixture
def local_scpi_tcp_server():
    """Fixture starting an in-process TCP server on 127.0.0.1 with dynamic port 0."""
    server = ThreadedTCPServer(("127.0.0.1", 0), MockSCPITCPServerHandler)
    ip, port = server.server_address

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(0.05)  # Allow socket to bind and start listening

    yield ip, port

    server.shutdown()
    server.server_close()


def test_tcp_transport_local_integration(local_scpi_tcp_server) -> None:
    """Verify real end-to-end TCP socket communication against local server."""
    host, port = local_scpi_tcp_server

    transport = TCPTransport(host=host, port=port, timeout=2.0)
    scpi = SCPIProtocol(transport=transport)

    assert not transport.is_connected
    transport.connect()
    assert transport.is_connected

    try:
        # Test IEEE 488.2 *IDN? query
        idn = scpi.idn()
        assert idn == "LabLink,MockServer,SN9999,v1.0"

        # Test system error check
        code, msg = scpi.get_system_error()
        assert code == 0
        assert msg == "No error"

        # Test custom query
        echo_resp = scpi.query("MEAS:VOLT?")
        assert echo_resp == "ECHO:MEAS:VOLT?"

    finally:
        transport.disconnect()
        assert not transport.is_connected
