"""Minimal custom toolset: subclass `FunctionToolset` (an `AbstractToolset`) with one tool."""

from __future__ import annotations

import httpx
from pydantic_ai import FunctionToolset


def _iss_now(http_timeout: float = 10.0) -> str:
    """Return the current latitude and longitude of the International Space Station."""
    response = httpx.get(
        "http://api.open-notify.org/iss-now.json",
        timeout=http_timeout,
    )
    response.raise_for_status()
    payload = response.json()
    position = payload["iss_position"]
    return f"latitude {position['latitude']}, longitude {position['longitude']}"


class IssOpenNotifyToolset(FunctionToolset):
    """One HTTP-backed tool; `FunctionToolset` supplies `get_tools` / `call_tool`."""

    def __init__(
        self,
        *,
        toolset_id: str | None = "iss_open_notify",
        httpx_timeout: float = 10.0,
        instructions: str | None = None,
    ) -> None:
        def iss_now() -> str:
            return _iss_now(httpx_timeout)

        iss_now.__doc__ = _iss_now.__doc__

        super().__init__(
            id=toolset_id,
            instructions=instructions
            or "Use iss_now when the user asks for the ISS position.",
            tools=[iss_now],
        )
