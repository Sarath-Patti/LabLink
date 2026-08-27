"""
LabLink VISA-Style Resource Abstraction.

Provides a PyVISA / NI-VISA compatible resource interface without requiring
external NI-VISA binary installations or hardware drivers.
Wraps LabLink BaseTransport implementations and SCPIProtocol logic.
"""

import re

from lablink.exceptions import VISAError
from lablink.logging import get_logger
from lablink.protocols.scpi import SCPIProtocol
from lablink.transport.base import BaseTransport
from lablink.transport.mock import MockTransport
from lablink.transport.serial import SerialTransport
from lablink.transport.tcp import TCPTransport

logger = get_logger("protocols.visa")


class VISAResource:
    """
    VISA-Style Instrument Resource.

    Provides standard VISA resource methods (write, read, query, clear, close)
    backed by LabLink's transport and SCPI protocol layers.
    """

    def __init__(self, resource_name: str, transport: BaseTransport) -> None:
        self.resource_name: str = resource_name
        self.transport: BaseTransport = transport
        self.scpi: SCPIProtocol = SCPIProtocol(transport=transport)

    @property
    def is_connected(self) -> bool:
        """Return connection state of underlying transport."""
        return self.transport.is_connected

    @property
    def timeout(self) -> float:
        """Return resource operation timeout in seconds."""
        return self.transport.timeout

    @timeout.setter
    def timeout(self, value: float) -> None:
        """Set resource operation timeout in seconds."""
        self.transport.timeout = value

    def open(self) -> None:
        """Open/connect resource transport."""
        self.transport.connect()

    def close(self) -> None:
        """Close/disconnect resource transport."""
        self.transport.disconnect()

    def write(self, command: str) -> None:
        """Write SCPI command to resource."""
        self.scpi.write(command)

    def read(self) -> str:
        """Read SCPI response from resource."""
        return self.scpi.read()

    def query(self, command: str) -> str:
        """Query resource with SCPI command."""
        return self.scpi.query(command)

    def clear(self) -> None:
        """Send status clear (*CLS) to resource."""
        self.scpi.clear()


class VISAResourceManager:
    """
    VISA Resource Manager for creating VISAResource instances from resource descriptor strings.
    """

    @classmethod
    def get_resource(
        cls,
        resource_name: str,
        timeout: float | None = None,
        open_connection: bool = False,
    ) -> VISAResource:
        """
        Parse VISA resource descriptor string and return an initialized VISAResource.

        Args:
            resource_name: VISA resource descriptor string.
            timeout: Optional operation timeout in seconds.
            open_connection: If True, connects the transport immediately. Defaults to False.
        """
        logger.info(f"Creating VISA resource: '{resource_name}'")
        transport = cls._create_transport_from_descriptor(resource_name)
        if timeout is not None:
            transport.timeout = timeout

        resource = VISAResource(resource_name=resource_name, transport=transport)
        if open_connection:
            resource.open()
        return resource

    @classmethod
    def open_resource(
        cls,
        resource_name: str,
        timeout: float | None = None,
        open_connection: bool = True,
    ) -> VISAResource:
        """
        Parse VISA resource descriptor string and return an opened VISAResource.

        Supported Formats:
            - TCPIP[board]::host::port[::SOCKET] (e.g. 'TCPIP0::192.168.1.100::5025::SOCKET')
            - ASRL[port]::baudrate[::INSTR] (e.g. 'ASRL1::9600::INSTR' or 'ASRL::/dev/ttyUSB0::9600::INSTR')
            - MOCK::[id]::INSTR (e.g. 'MOCK::SIMULATOR::INSTR')
        """
        return cls.get_resource(
            resource_name=resource_name, timeout=timeout, open_connection=open_connection
        )

    @classmethod
    def _create_transport_from_descriptor(cls, resource_name: str) -> BaseTransport:
        descriptor = resource_name.strip()

        # Match TCPIP descriptors: TCPIP[board]::host::port[::SOCKET]
        tcp_match = re.match(r"^TCPIP\d*::([^:]+)::(\d+)(?:::SOCKET)?$", descriptor, re.IGNORECASE)
        if tcp_match:
            host = tcp_match.group(1)
            port = int(tcp_match.group(2))
            return TCPTransport(host=host, port=port)

        # Match ASRL descriptors: ASRL[port_or_name]::[baudrate][::INSTR]
        serial_match = re.match(
            r"^ASRL(?:\d+|::[^:]+)?::(\d+)(?:::\w+)?$", descriptor, re.IGNORECASE
        )
        if serial_match:
            baudrate = int(serial_match.group(1))
            return SerialTransport(port="COM1", baudrate=baudrate)

        # Match MOCK descriptors: MOCK::[id]::INSTR
        mock_match = re.match(r"^MOCK::[^:]+::INSTR$", descriptor, re.IGNORECASE)
        if mock_match:
            return MockTransport()

        raise VISAError(f"Unsupported or malformed VISA resource descriptor: '{resource_name}'")
