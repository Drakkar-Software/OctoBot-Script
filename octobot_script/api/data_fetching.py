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

import octobot_backtesting.api as backtesting_api
import octobot_commons.symbols as commons_symbols
import octobot_commons.enums as commons_enums
import octobot_trading.enums as trading_enums
import octobot_script.internal.octobot_mocks as octobot_mocks


def _ensure_ms_timestamp(timestamp):
    if timestamp is None:
        return timestamp
    if timestamp < 16737955050:  # Friday 28 May 2500 07:57:30
        return timestamp * 1000


async def historical_data(symbol, timeframe, exchange="binance", exchange_type=trading_enums.ExchangeTypes.SPOT.value,
                          start_timestamp=None, end_timestamp=None):
    symbols = [symbol]
    time_frames = [commons_enums.TimeFrames(timeframe)]
    data_collector_instance = backtesting_api.exchange_historical_data_collector_factory(
        exchange,
        trading_enums.ExchangeTypes(exchange_type),
        octobot_mocks.get_tentacles_config(),
        [commons_symbols.parse_symbol(symbol) for symbol in symbols],
        time_frames=time_frames,
        start_timestamp=_ensure_ms_timestamp(start_timestamp),
        end_timestamp=_ensure_ms_timestamp(end_timestamp)
    )
    return await backtesting_api.initialize_and_run_data_collector(data_collector_instance)


async def get_data(symbol, time_frame, exchange="binance", exchange_type=trading_enums.ExchangeTypes.SPOT.value,
                   start_timestamp=None, end_timestamp=None, data_file=None):
    data = data_file or \
           await historical_data(symbol, timeframe=time_frame, exchange=exchange, exchange_type=exchange_type,
                                 start_timestamp=start_timestamp, end_timestamp=end_timestamp)
    return await backtesting_api.create_and_init_backtest_data(
        [data],
        octobot_mocks.get_config(),
        octobot_mocks.get_tentacles_config(),
    )
