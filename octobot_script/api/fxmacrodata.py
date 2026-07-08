#  This file is part of OctoBot-Script (https://github.com/Drakkar-Software/OctoBot-Script)
#  Copyright (c) 2023 Drakkar-Software, All rights reserved.
#
#  OctoBot is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  OctoBot is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public
#  License along with OctoBot-Script. If not, see <https://www.gnu.org/licenses/>.

import os
from typing import Any, Optional

import aiohttp

FXMACRODATA_BASE_URL = "https://fxmacrodata.com/api/v1"


async def fxmacrodata_release_calendar(
    currency: str = "usd",
    limit: int = 50,
    min_tier: Optional[int] = 1,
) -> list[dict[str, Any]]:
    """Fetch official macro release-calendar events from FXMacroData."""

    limit_count = max(1, min(int(limit), 100))
    params: dict[str, str] = {"limit": str(limit_count)}
    api_key = os.getenv("FXMACRODATA_API_KEY")
    if api_key:
        params["api_key"] = api_key

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{FXMACRODATA_BASE_URL}/calendar/{currency.lower()}",
            params=params,
            timeout=aiohttp.ClientTimeout(total=20),
        ) as response:
            response.raise_for_status()
            payload = await response.json()

    events = payload.get("data", [])
    if min_tier is None:
        return events[:limit_count]
    return [
        event
        for event in events
        if int(event.get("market_tier") or 99) <= min_tier
    ][:limit_count]
