"""
Unit tests for DUT model abstraction.
"""

import pytest

from lablink.manufacturing.dut import DUT, DUTStatus


def test_dut_creation_and_attributes() -> None:
    dut = DUT(serial_number="SN-TEST-1234", part_number="PN-OPT-100G", hardware_revision="RevB")
    assert dut.serial_number == "SN-TEST-1234"
    assert dut.part_number == "PN-OPT-100G"
    assert dut.hardware_revision == "RevB"
    assert dut.status == DUTStatus.UNTESTED


def test_dut_invalid_empty_serial() -> None:
    with pytest.raises(ValueError, match="serial_number must be a non-empty string"):
        DUT(serial_number="")


def test_dut_dictionary_export() -> None:
    dut = DUT(serial_number="SN-DICT-01")
    d = dut.to_dict()
    assert d["serial_number"] == "SN-DICT-01"
    assert d["status"] == "Untested"
