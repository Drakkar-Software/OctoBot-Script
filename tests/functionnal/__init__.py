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
