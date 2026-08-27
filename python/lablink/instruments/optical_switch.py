"""
LabLink Optical Switch Instrument Abstraction.

Provides automated control for optical channel routing and port switching
over SCPI protocol and BaseTransport.
"""

from lablink.instruments.base import BaseInstrument
from lablink.logging import get_logger

logger = get_logger("instruments.optical_switch")


class OpticalSwitch(BaseInstrument):
    """
    Software representation of an Optical Switch test instrument.
    """

    def set_route(self, channel: int) -> None:
        """
        Set active optical switch channel route.

        Args:
            channel: Target 1-indexed channel integer.
        """
        if channel < 1:
            raise ValueError(f"Invalid channel route {channel}; must be >= 1.")

        logger.info(f"Setting Optical Switch route to channel {channel}")
        self.write(f"ROUTE:SET {channel}")

    def get_route(self) -> int:
        """
        Query currently active optical switch channel route.

        Returns:
            Active channel integer.
        """
        resp = self.query("ROUTE?")
        return int(resp.strip())

    def get_channel_count(self) -> int:
        """
        Query total number of supported channels on the optical switch.

        Returns:
            Channel count integer.
        """
        resp = self.query("ROUTE:CHAN:COUNT?")
        return int(resp.strip())
