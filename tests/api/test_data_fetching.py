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

import pytest
import mock

import octobot_commons.enums as commons_enums
import octobot_trading.enums as trading_enums
import octobot_backtesting.api as backtesting_api
import octobot_script as obs
import octobot_script.api.data_fetching as data_fetching

from tests import mocked_config, TEST_CONFIG, TEST_TENTACLES_CONFIG


# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_historical_data():
    with (
        mock.patch.object(
            backtesting_api,
            "find_matching_data_file",
            mock.AsyncMock(return_value=None),
        ) as find_matching_data_file_mock,
        mock.patch.object(
            backtesting_api,
            "initialize_and_run_data_collector",
            mock.AsyncMock(return_value="data"),
        ) as initialize_and_run_data_collector_mock,
    ):
        assert (
            await obs.historical_data(
                "BTC/USDT", commons_enums.TimeFrames.ONE_DAY.value
            )
            == "data"
        )
        find_matching_data_file_mock.assert_awaited_once()
        initialize_and_run_data_collector_mock.assert_awaited_once()


async def test_social_historical_data():
    with (
        mock.patch.object(
            backtesting_api,
            "find_matching_data_file",
            mock.AsyncMock(return_value=None),
        ) as find_matching_data_file_mock,
        mock.patch.object(
            backtesting_api,
            "initialize_and_run_data_collector",
            mock.AsyncMock(return_value="social_data"),
        ) as initialize_and_run_data_collector_mock,
    ):
        assert (
            await obs.social_historical_data(
                ["AlternativeMeServiceFeed"],
                sources=["topic_fear_and_greed"],
                start_timestamp=1700000000,
                end_timestamp=1710000000,
            )
            == "social_data"
        )
        find_matching_data_file_mock.assert_awaited_once()
        initialize_and_run_data_collector_mock.assert_awaited_once()


async def test_get_data(mocked_config):
    with (
        mock.patch.object(
            data_fetching, "historical_data", mock.AsyncMock(return_value="data")
        ) as historical_data_mock,
        mock.patch.object(
            backtesting_api,
            "create_and_init_backtest_data",
            mock.AsyncMock(return_value="backtest_data"),
        ) as create_and_init_backtest_data_mock,
    ):
        assert (
            await obs.get_data("BTC/USDT", commons_enums.TimeFrames.ONE_DAY.value)
            == "backtest_data"
        )
        historical_data_mock.assert_awaited_once_with(
            "BTC/USDT",
            timeframe=commons_enums.TimeFrames.ONE_DAY.value,
            exchange="binance",
            exchange_type=trading_enums.ExchangeTypes.SPOT.value,
            start_timestamp=None,
            end_timestamp=None,
            tentacles_config=None,
            profile_id=None,
        )
        create_and_init_backtest_data_mock.assert_awaited_once_with(
            ["data"],
            TEST_CONFIG,
            TEST_TENTACLES_CONFIG,
            use_accurate_price_time_frame=True,
        )
        historical_data_mock.reset_mock()
        create_and_init_backtest_data_mock.reset_mock()
        assert (
            await obs.get_data(
                "BTC/USDT",
                commons_enums.TimeFrames.ONE_DAY.value,
                data_file="existing_file",
            )
            == "backtest_data"
        )
        historical_data_mock.assert_not_awaited()
        create_and_init_backtest_data_mock.assert_awaited_once_with(
            ["existing_file"],
            TEST_CONFIG,
            TEST_TENTACLES_CONFIG,
            use_accurate_price_time_frame=True,
        )


async def test_get_data_with_social_services(mocked_config):
    with (
        mock.patch.object(
            data_fetching,
            "historical_data",
            mock.AsyncMock(return_value="exchange_data"),
        ) as historical_data_mock,
        mock.patch.object(
            data_fetching,
            "social_historical_data",
            mock.AsyncMock(return_value="social_data"),
        ) as social_historical_data_mock,
        mock.patch.object(
            backtesting_api,
            "create_and_init_backtest_data",
            mock.AsyncMock(return_value="backtest_data"),
        ) as create_and_init_backtest_data_mock,
    ):
        assert (
            await obs.get_data(
                "BTC/USDT",
                commons_enums.TimeFrames.ONE_DAY.value,
                social_services=["CoindeskServiceFeed"],
                social_sources=["news"],
                start_timestamp=1700000000,
                end_timestamp=1710000000,
            )
            == "backtest_data"
        )
        historical_data_mock.assert_awaited_once()
        social_historical_data_mock.assert_awaited_once_with(
            ["CoindeskServiceFeed"],
            sources=["news"],
            symbols=None,
            start_timestamp=1700000000,
            end_timestamp=1710000000,
            tentacles_config=None,
            profile_id=None,
        )
        create_and_init_backtest_data_mock.assert_awaited_once_with(
            ["exchange_data", "social_data"],
            TEST_CONFIG,
            TEST_TENTACLES_CONFIG,
            use_accurate_price_time_frame=True,
        )


async def test_get_data_with_social_data_files(mocked_config):
    with (
        mock.patch.object(
            data_fetching,
            "historical_data",
            mock.AsyncMock(return_value="exchange_data"),
        ) as historical_data_mock,
        mock.patch.object(
            data_fetching,
            "social_historical_data",
            mock.AsyncMock(return_value="social_data"),
        ) as social_historical_data_mock,
        mock.patch.object(
            backtesting_api,
            "create_and_init_backtest_data",
            mock.AsyncMock(return_value="backtest_data"),
        ) as create_and_init_backtest_data_mock,
    ):
        assert (
            await obs.get_data(
                "BTC/USDT",
                commons_enums.TimeFrames.ONE_DAY.value,
                social_data_files=["social_file_1", "social_file_2"],
            )
            == "backtest_data"
        )
        historical_data_mock.assert_awaited_once()
        social_historical_data_mock.assert_not_awaited()
        create_and_init_backtest_data_mock.assert_awaited_once_with(
            ["exchange_data", "social_file_1", "social_file_2"],
            TEST_CONFIG,
            TEST_TENTACLES_CONFIG,
            use_accurate_price_time_frame=True,
        )


async def test_get_data_with_auto_social_services(mocked_config):
    with (
        mock.patch.object(
            data_fetching,
            "historical_data",
            mock.AsyncMock(return_value="exchange_data"),
        ) as historical_data_mock,
        mock.patch.object(
            data_fetching,
            "social_historical_data",
            mock.AsyncMock(return_value="social_data"),
        ) as social_historical_data_mock,
        mock.patch.object(
            data_fetching.octobot_mocks,
            "get_activated_social_services",
            mock.Mock(return_value=["AlternativeMeServiceFeed"]),
        ) as get_activated_social_services_mock,
        mock.patch.object(
            backtesting_api,
            "create_and_init_backtest_data",
            mock.AsyncMock(return_value="backtest_data"),
        ) as create_and_init_backtest_data_mock,
    ):
        assert (
            await obs.get_data(
                "BTC/USDT",
                commons_enums.TimeFrames.ONE_DAY.value,
                social_sources=["topic_fear_and_greed"],
            )
            == "backtest_data"
        )
        historical_data_mock.assert_awaited_once()
        get_activated_social_services_mock.assert_called_once_with(
            None, None, requested_sources=["topic_fear_and_greed"]
        )
        social_historical_data_mock.assert_awaited_once_with(
            ["AlternativeMeServiceFeed"],
            sources=["topic_fear_and_greed"],
            symbols=None,
            start_timestamp=None,
            end_timestamp=None,
            tentacles_config=None,
            profile_id=None,
        )
        create_and_init_backtest_data_mock.assert_awaited_once_with(
            ["exchange_data", "social_data"],
            TEST_CONFIG,
            TEST_TENTACLES_CONFIG,
            use_accurate_price_time_frame=True,
        )


async def test_get_data_with_tentacles_config(mocked_config):
    tentacles_config = {"services": {"AlternativeMeServiceFeed": True}}
    with (
        mock.patch.object(
            data_fetching,
            "historical_data",
            mock.AsyncMock(return_value="exchange_data"),
        ) as historical_data_mock,
        mock.patch.object(
            data_fetching.octobot_mocks,
            "get_activated_social_services",
            mock.Mock(return_value=[]),
        ) as get_activated_social_services_mock,
        mock.patch.object(
            data_fetching.octobot_mocks,
            "get_tentacles_config",
            mock.Mock(return_value=TEST_TENTACLES_CONFIG),
        ) as get_tentacles_config_mock,
        mock.patch.object(
            backtesting_api,
            "create_and_init_backtest_data",
            mock.AsyncMock(return_value="backtest_data"),
        ) as create_and_init_backtest_data_mock,
    ):
        assert (
            await obs.get_data(
                "BTC/USDT",
                commons_enums.TimeFrames.ONE_DAY.value,
                tentacles_config=tentacles_config,
            )
            == "backtest_data"
        )
        historical_data_mock.assert_awaited_once_with(
            "BTC/USDT",
            timeframe=commons_enums.TimeFrames.ONE_DAY.value,
            exchange="binance",
            exchange_type=trading_enums.ExchangeTypes.SPOT.value,
            start_timestamp=None,
            end_timestamp=None,
            tentacles_config=tentacles_config,
            profile_id=None,
        )
        get_activated_social_services_mock.assert_called_once_with(
            tentacles_config, None, requested_sources=None
        )
        get_tentacles_config_mock.assert_called_once_with(
            tentacles_config, None, activate_strategy_tentacles=False
        )
        create_and_init_backtest_data_mock.assert_awaited_once_with(
            ["exchange_data"],
            TEST_CONFIG,
            TEST_TENTACLES_CONFIG,
            use_accurate_price_time_frame=True,
        )


async def test_get_data_with_profile_id(mocked_config):
    profile_id = "profile-1"
    with (
        mock.patch.object(
            data_fetching,
            "historical_data",
            mock.AsyncMock(return_value="exchange_data"),
        ) as historical_data_mock,
        mock.patch.object(
            data_fetching.octobot_mocks,
            "get_activated_social_services",
            mock.Mock(return_value=[]),
        ) as get_activated_social_services_mock,
        mock.patch.object(
            data_fetching.octobot_mocks,
            "get_tentacles_config",
            mock.Mock(return_value=TEST_TENTACLES_CONFIG),
        ) as get_tentacles_config_mock,
        mock.patch.object(
            backtesting_api,
            "create_and_init_backtest_data",
            mock.AsyncMock(return_value="backtest_data"),
        ) as create_and_init_backtest_data_mock,
    ):
        assert (
            await obs.get_data(
                "BTC/USDT",
                commons_enums.TimeFrames.ONE_DAY.value,
                profile_id=profile_id,
            )
            == "backtest_data"
        )
        historical_data_mock.assert_awaited_once_with(
            "BTC/USDT",
            timeframe=commons_enums.TimeFrames.ONE_DAY.value,
            exchange="binance",
            exchange_type=trading_enums.ExchangeTypes.SPOT.value,
            start_timestamp=None,
            end_timestamp=None,
            tentacles_config=None,
            profile_id=profile_id,
        )
        get_activated_social_services_mock.assert_called_once_with(
            None, profile_id, requested_sources=None
        )
        get_tentacles_config_mock.assert_called_once_with(
            None, profile_id, activate_strategy_tentacles=False
        )
        create_and_init_backtest_data_mock.assert_awaited_once_with(
            ["exchange_data"],
            TEST_CONFIG,
            TEST_TENTACLES_CONFIG,
            use_accurate_price_time_frame=True,
        )


async def test_get_data_with_profile_id_and_tentacles_config_raises():
    with pytest.raises(ValueError):
        await obs.get_data(
            "BTC/USDT",
            commons_enums.TimeFrames.ONE_DAY.value,
            tentacles_config={"any": {}},
            profile_id="profile-1",
        )
