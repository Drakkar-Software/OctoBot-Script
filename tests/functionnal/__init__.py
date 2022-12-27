#  This file is part of OctoBot-Pro (https://github.com/Drakkar-Software/OctoBot-Pro)
#  Copyright (c) 2022 Drakkar-Software, All rights reserved.
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
#  License along with OctoBot-Pro. If not, see <https://www.gnu.org/licenses/>.

import pytest_asyncio
import os
import octobot_pro as op


# only load config once
BACKTESTING_FILES_DIR = os.path.join("tests", "test_util")
ONE_DAY_BTC_USDT_DATA = os.path.join(BACKTESTING_FILES_DIR, "ExchangeHistoryDataCollector_1669821305.9084802.data")


@pytest_asyncio.fixture
async def one_day_btc_usdt_data():
    data = None
    try:
        data = await op.get_data("BTC/USDT", "1d", start_timestamp=1505606400, data_file=ONE_DAY_BTC_USDT_DATA)
        yield data
    finally:
        if data is not None:
            await data.stop()
