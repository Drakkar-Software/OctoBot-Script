import pytest
import mock

import octobot_commons.enums as commons_enums
import octobot_trading.enums as trading_enums
import octobot_backtesting.api as backtesting_api
import octobot_pro as op
import octobot_pro.api.data_fetching as data_fetching

from tests import mocked_config, TEST_CONFIG, TEST_TENTACLES_CONFIG


# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_historical_data():
    with mock.patch.object(backtesting_api, "initialize_and_run_data_collector", mock.AsyncMock(return_value="data")) \
         as initialize_and_run_data_collector_mock:
        assert await op.historical_data("BTC/USDT", commons_enums.TimeFrames.ONE_DAY.value) == "data"
        initialize_and_run_data_collector_mock.assert_awaited_once()


async def test_get_data(mocked_config):
    with mock.patch.object(data_fetching, "historical_data",
                           mock.AsyncMock(return_value="data")) as historical_data_mock, \
            mock.patch.object(backtesting_api, "create_and_init_backtest_data",
                              mock.AsyncMock(return_value="backtest_data")) as create_and_init_backtest_data_mock:
        assert await op.get_data("BTC/USDT", commons_enums.TimeFrames.ONE_DAY.value) == "backtest_data"
        historical_data_mock.assert_awaited_once_with(
            "BTC/USDT",
            timeframe=commons_enums.TimeFrames.ONE_DAY.value,
            exchange="binance",
            exchange_type=trading_enums.ExchangeTypes.SPOT.value,
            start_timestamp=None,
            end_timestamp=None,
        )
        create_and_init_backtest_data_mock.assert_awaited_once_with(
            ["data"],
            TEST_CONFIG,
            TEST_TENTACLES_CONFIG
        )
        historical_data_mock.reset_mock()
        create_and_init_backtest_data_mock.reset_mock()
        assert await op.get_data("BTC/USDT", commons_enums.TimeFrames.ONE_DAY.value, data_file="existing_file") \
               == "backtest_data"
        historical_data_mock.assert_not_awaited()
        create_and_init_backtest_data_mock.assert_awaited_once_with(
            ["existing_file"],
            TEST_CONFIG,
            TEST_TENTACLES_CONFIG
        )

