"""
LabLink Instrument Abstraction Package.

Provides high-level OOP instrument classes for optical power meters,
optical switches, and optical oscilloscopes.
"""

from lablink.instruments.base import BaseInstrument
from lablink.instruments.optical_oscilloscope import OpticalOscilloscope, WaveformData
from lablink.instruments.optical_power_meter import OpticalPowerMeter
from lablink.instruments.optical_switch import OpticalSwitch

__all__ = [
    "BaseInstrument",
    "OpticalOscilloscope",
    "OpticalPowerMeter",
    "OpticalSwitch",
    "WaveformData",
]
