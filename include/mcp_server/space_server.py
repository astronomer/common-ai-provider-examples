"""Tiny stdio MCP server exposing a few space-logistics tools.

Launched by the `mcp_stdio_space` Airflow connection:
    command = python
    args    = ["/usr/local/airflow/include/mcp_server/space_server.py"]
"""

from __future__ import annotations

import csv
from pathlib import Path

from mcp.server.fastmcp import FastMCP

CSV_DIR = Path(__file__).parent.parent / "csvs"

mcp = FastMCP("space-logistics")


@mcp.tool()
def list_planets() -> list[dict]:
    """Return every row of planets.csv."""
    with (CSV_DIR / "planets.csv").open() as fh:
        return list(csv.DictReader(fh))


@mcp.tool()
def list_spacecraft(status: str | None = None) -> list[dict]:
    """Return spacecraft, optionally filtered by current_status."""
    with (CSV_DIR / "spacecraft.csv").open() as fh:
        rows = list(csv.DictReader(fh))
    if status:
        rows = [r for r in rows if r["current_status"] == status]
    return rows


@mcp.tool()
def count_stations_by_planet() -> dict[str, int]:
    """Return { planet_id -> number of space stations in its orbit }."""
    with (CSV_DIR / "space_stations.csv").open() as fh:
        rows = list(csv.DictReader(fh))
    counts: dict[str, int] = {}
    for r in rows:
        pid = r.get("planet_id") or "unknown"
        counts[pid] = counts.get(pid, 0) + 1
    return counts


if __name__ == "__main__":
    mcp.run(transport="stdio")
