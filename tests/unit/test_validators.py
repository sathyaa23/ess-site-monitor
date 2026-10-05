"""
Unit tests - test pure validation logic in isolation.

No FastAPI, no HTTP, no store. Just: given an input, is the output correct?
These are the fastest tests and there are the most of them (base of the pyramid).
"""

import pytest

from app.validators import (
    Reading,
    Severity,
    is_voltage_valid,
    is_temperature_valid,
    is_soc_valid,
    classify_temperature,
    validate_reading,
)


# --- Voltage ---
# parametrize lets one test function cover many cases - a key pytest feature.
@pytest.mark.parametrize("voltage,expected", [
    (400.0, True),     # normal
    (0.0, True),       # lower boundary
    (1000.0, True),    # upper boundary
    (-5.0, False),     # below range
    (1500.0, False),   # above range
])
def test_voltage_validation(voltage, expected):
    assert is_voltage_valid(voltage) is expected


# --- Temperature ---
@pytest.mark.parametrize("temp,expected", [
    (25.0, True),
    (-20.0, True),     # lower boundary
    (60.0, True),      # upper boundary
    (-30.0, False),    # too cold
    (75.0, False),     # too hot
])
def test_temperature_validation(temp, expected):
    assert is_temperature_valid(temp) is expected


# --- State of charge ---
@pytest.mark.parametrize("soc,expected", [
    (80.0, True),
    (0.0, True),
    (100.0, True),
    (-1.0, False),
    (101.0, False),
])
def test_soc_validation(soc, expected):
    assert is_soc_valid(soc) is expected


# --- Severity classification ---
def test_classify_temperature_ok():
    assert classify_temperature(25.0) == Severity.OK


def test_classify_temperature_warning():
    # 57 is within 5 degrees of the 60 ceiling -> warning
    assert classify_temperature(57.0) == Severity.WARNING


def test_classify_temperature_critical():
    assert classify_temperature(80.0) == Severity.CRITICAL


# --- Full reading validation ---
def test_validate_good_reading():
    reading = Reading("SITE-01", voltage=400.0, temperature=25.0, state_of_charge=80.0)
    result = validate_reading(reading)
    assert result["valid"] is True
    assert result["failed_fields"] == []
    assert result["severity"] == "ok"


def test_validate_bad_voltage_reading():
    reading = Reading("SITE-01", voltage=5000.0, temperature=25.0, state_of_charge=80.0)
    result = validate_reading(reading)
    assert result["valid"] is False
    assert "voltage" in result["failed_fields"]


def test_validate_multiple_failures():
    reading = Reading("SITE-01", voltage=5000.0, temperature=90.0, state_of_charge=200.0)
    result = validate_reading(reading)
    assert result["valid"] is False
    assert set(result["failed_fields"]) == {"voltage", "temperature", "state_of_charge"}
    assert result["severity"] == "critical"
