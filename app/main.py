"""
ESS Site Monitor - FastAPI service.

Exposes:
  - POST /telemetry     : validate a battery reading (JSON API)
  - GET  /health        : liveness check (used by Docker healthcheck + smoke tests)
  - GET  /dashboard     : minimal HTML UI (target for Playwright + Selenium E2E tests)
  - GET  /docs          : auto-generated Swagger UI (FastAPI built-in)

The in-memory store stands in for a database. Keeping it in-memory means the
project runs anywhere with zero setup, while still exercising the full
request -> validate -> store -> respond path for integration tests.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from app.validators import Reading, validate_reading

app = FastAPI(
    title="ESS Site Monitor",
    description="Validates battery energy-storage telemetry and flags anomalies.",
    version="1.0.0",
)

# In-memory store standing in for a database.
_readings_store: list[dict] = []


class TelemetryIn(BaseModel):
    """Incoming telemetry payload. Pydantic enforces types + basic bounds."""
    site_id: str = Field(..., examples=["SITE-TX-01"])
    voltage: float = Field(..., examples=[400.0])
    temperature: float = Field(..., examples=[25.0])
    state_of_charge: float = Field(..., examples=[80.0])


@app.get("/health")
def health() -> dict:
    """Liveness probe. Cheap, no dependencies - ideal for smoke tests."""
    return {"status": "ok", "readings_count": len(_readings_store)}


@app.post("/telemetry", status_code=201)
def ingest_telemetry(payload: TelemetryIn) -> dict:
    """
    Validate an incoming reading. Rejects anomalous readings with 422 so a
    client (or test) can assert on the failure, mirroring how a real
    monitoring pipeline would refuse bad data.
    """
    reading = Reading(
        site_id=payload.site_id,
        voltage=payload.voltage,
        temperature=payload.temperature,
        state_of_charge=payload.state_of_charge,
    )
    result = validate_reading(reading)

    if not result["valid"]:
        # 422 = the request was well-formed but the values are invalid
        raise HTTPException(status_code=422, detail=result)

    _readings_store.append(result)
    return {"status": "saved", **result}


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard() -> str:
    """
    Minimal dashboard UI. Intentionally simple, stable element IDs so both
    Playwright and Selenium can drive it reliably.
    """
    return """
    <!DOCTYPE html>
    <html>
    <head><title>ESS Site Monitor</title></head>
    <body>
        <h1 id="title">ESS Site Monitor</h1>
        <form id="telemetry-form" onsubmit="return false;">
            <input id="site-input" placeholder="Site ID" value="SITE-TX-01" />
            <input id="voltage-input" placeholder="Voltage" />
            <input id="temp-input" placeholder="Temperature" />
            <input id="soc-input" placeholder="State of Charge" />
            <button id="submit-btn" onclick="submitReading()">Submit</button>
        </form>
        <div id="result"></div>
        <script>
            async function submitReading() {
                const payload = {
                    site_id: document.getElementById('site-input').value,
                    voltage: parseFloat(document.getElementById('voltage-input').value),
                    temperature: parseFloat(document.getElementById('temp-input').value),
                    state_of_charge: parseFloat(document.getElementById('soc-input').value)
                };
                const res = await fetch('/telemetry', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                const el = document.getElementById('result');
                if (res.status === 201) {
                    el.textContent = 'Reading saved: ' + data.severity;
                    el.className = 'success';
                } else {
                    el.textContent = 'Invalid reading: ' + (data.detail.failed_fields || []).join(', ');
                    el.className = 'error';
                }
            }
        </script>
    </body>
    </html>
    """
