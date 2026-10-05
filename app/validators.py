"""
Pure validation functions for battery ESS (Energy Storage System) telemetry.

These are deliberately pure functions (no I/O, no state) so they can be
unit-tested in isolation. This mirrors how AEROS-style monitoring software
validates incoming readings from grid-scale battery sites before storing
or acting on them.

Safe operating ranges are based on typical Li-ion / LFP ESS parameters.
"""

from enum import Enum
from dataclasses import dataclass


# --- Safe operating ranges for a battery cell/rack ---
# These constants make the "why this number" answerable in an interview.
VOLTAGE_MIN = 0.0        # volts
VOLTAGE_MAX = 1000.0     # volts (grid-scale rack level)
TEMP_MIN = -20.0         # celsius (below this = cold-weather fault)
TEMP_MAX = 60.0          # celsius (above this = thermal runaway risk)
SOC_MIN = 0.0            # state of charge %
SOC_MAX = 100.0          # state of charge %


class Severity(str, Enum):
    """Severity of an anomaly, so downstream systems can prioritize."""
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Reading:
    """A single telemetry reading from a battery site."""
    site_id: str
    voltage: float
    temperature: float
    state_of_charge: float


def is_voltage_valid(voltage: float) -> bool:
    """Voltage must sit within the rack's safe operating window."""
    return VOLTAGE_MIN <= voltage <= VOLTAGE_MAX


def is_temperature_valid(temperature: float) -> bool:
    """Temperature outside range indicates a cooling or thermal fault."""
    return TEMP_MIN <= temperature <= TEMP_MAX


def is_soc_valid(state_of_charge: float) -> bool:
    """State of charge is a percentage, so it must be 0-100."""
    return SOC_MIN <= state_of_charge <= SOC_MAX


def classify_temperature(temperature: float) -> Severity:
    """
    Classify how dangerous a temperature reading is.
    Warning band gives operators lead time before a critical fault.
    """
    if temperature > TEMP_MAX or temperature < TEMP_MIN:
        return Severity.CRITICAL
    # within 5 degrees of the ceiling = early warning
    if temperature > (TEMP_MAX - 5):
        return Severity.WARNING
    return Severity.OK


def validate_reading(reading: Reading) -> dict:
    """
    Validate a full reading and return a structured result.

    Returns a dict with overall validity, a severity, and the list of
    fields that failed - the kind of structured output a monitoring
    dashboard would consume.
    """
    errors = []

    if not is_voltage_valid(reading.voltage):
        errors.append("voltage")
    if not is_temperature_valid(reading.temperature):
        errors.append("temperature")
    if not is_soc_valid(reading.state_of_charge):
        errors.append("state_of_charge")

    severity = classify_temperature(reading.temperature)
    if errors and severity == Severity.OK:
        # something failed but temp was fine -> at least a warning
        severity = Severity.WARNING

    return {
        "site_id": reading.site_id,
        "valid": len(errors) == 0,
        "severity": severity.value,
        "failed_fields": errors,
    }
