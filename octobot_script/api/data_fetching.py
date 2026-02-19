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

import datetime

import octobot_backtesting.api as backtesting_api
import octobot_commons.symbols as commons_symbols
import octobot_commons.enums as commons_enums
import octobot_trading.enums as trading_enums
import octobot_script.internal.octobot_mocks as octobot_mocks


def _validate_tentacles_source(tentacles_config, profile_id):
    if tentacles_config is not None and profile_id is not None:
        raise ValueError("Only one of tentacles_config or profile_id can be provided.")


def _ensure_ms_timestamp(timestamp):
    if timestamp is None:
        return timestamp
    if timestamp < 16737955050:  # Friday 28 May 2500 07:57:30
        return timestamp * 1000


def _yesterday_midnight_ms() -> int:
    """Return today at 00:00:00 UTC (= end of yesterday) in milliseconds.
    Used as a stable default end_timestamp so data files collected on the
    same calendar day share an identical end boundary and can be cached."""
    today_midnight = datetime.datetime.now(datetime.timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return int(today_midnight.timestamp() * 1000)


def _resolve_end_timestamp_ms(end_timestamp) -> int:
    if end_timestamp is None:
        return _yesterday_midnight_ms()
    return _ensure_ms_timestamp(end_timestamp)


async def historical_data(
    symbol,
    timeframe,
    exchange="binance",
    exchange_type=trading_enums.ExchangeTypes.SPOT.value,
    start_timestamp=None,
    end_timestamp=None,
    tentacles_config=None,
    profile_id=None,
):
    _validate_tentacles_source(tentacles_config, profile_id)
    symbols = [symbol]
    time_frames = [commons_enums.TimeFrames(timeframe)]
    start_timestamp_ms = _ensure_ms_timestamp(start_timestamp)
    end_timestamp_ms = _resolve_end_timestamp_ms(end_timestamp)
    existing_file = await backtesting_api.find_matching_data_file(
        exchange_name=exchange,
        symbols=symbols,
        time_frames=time_frames,
        start_timestamp=start_timestamp_ms,
        end_timestamp=end_timestamp_ms,
    )
    if existing_file:
        return existing_file
    data_collector_instance = (
        backtesting_api.exchange_historical_data_collector_factory(
            exchange,
            trading_enums.ExchangeTypes(exchange_type),
            octobot_mocks.get_tentacles_config(
                tentacles_config, profile_id, activate_strategy_tentacles=False
            ),
            [commons_symbols.parse_symbol(symbol) for symbol in symbols],
            time_frames=time_frames,
            start_timestamp=start_timestamp_ms,
            end_timestamp=end_timestamp_ms,
        )
    )
    return await backtesting_api.initialize_and_run_data_collector(
        data_collector_instance
    )


async def social_historical_data(
    services: list[str],
    sources: list[str] | None = None,
    symbols: list[str] | None = None,
    start_timestamp=None,
    end_timestamp=None,
    tentacles_config=None,
    profile_id=None,
):
    _validate_tentacles_source(tentacles_config, profile_id)
    start_timestamp_ms = _ensure_ms_timestamp(start_timestamp)
    end_timestamp_ms = _resolve_end_timestamp_ms(end_timestamp)
    existing_file = await backtesting_api.find_matching_data_file(
        services=services,
        symbols=symbols or [],
        start_timestamp=start_timestamp_ms,
        end_timestamp=end_timestamp_ms,
    )
    if existing_file:
        return existing_file
    data_collector_instance = backtesting_api.social_historical_data_collector_factory(
        services=services,
        tentacles_setup_config=octobot_mocks.get_tentacles_config(
            tentacles_config, profile_id, activate_strategy_tentacles=False
        ),
        sources=sources,
        symbols=[commons_symbols.parse_symbol(symbol) for symbol in symbols]
        if symbols
        else None,
        start_timestamp=start_timestamp_ms,
        end_timestamp=end_timestamp_ms,
        config=octobot_mocks.get_config(),
    )
    return await backtesting_api.initialize_and_run_data_collector(
        data_collector_instance
    )


async def get_data(
    symbol,
    time_frame,
    exchange="binance",
    exchange_type=trading_enums.ExchangeTypes.SPOT.value,
    start_timestamp=None,
    end_timestamp=None,
    data_file=None,
    social_data_files: list[str] | None = None,
    social_services: list[str] | None = None,
    social_sources: list[str] | None = None,
    social_symbols: list[str] | None = None,
    tentacles_config=None,
    profile_id=None,
):
    _validate_tentacles_source(tentacles_config, profile_id)
    data_files = (
        [data_file]
        if data_file
        else [
            await historical_data(
                symbol,
                timeframe=time_frame,
                exchange=exchange,
                exchange_type=exchange_type,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                tentacles_config=tentacles_config,
                profile_id=profile_id,
            )
        ]
    )

    if social_data_files is not None:
        data_files.extend(social_data_files)
    elif (
        profile_id is not None
        or social_sources is not None
        or tentacles_config is not None
    ):
        social_services = (
            social_services
            if social_services is not None
            else octobot_mocks.get_activated_social_services(
                tentacles_config, profile_id, requested_sources=social_sources
            )
        )
    if social_services:
        for service in social_services:
            data_files.append(
                await social_historical_data(
                    [service],
                    sources=social_sources,
                    symbols=social_symbols,
                    start_timestamp=start_timestamp,
                    end_timestamp=end_timestamp,
                    tentacles_config=tentacles_config,
                    profile_id=profile_id,
                )
            )

    return await backtesting_api.create_and_init_backtest_data(
        data_files,
        octobot_mocks.get_config(),
        octobot_mocks.get_tentacles_config(
            tentacles_config, profile_id, activate_strategy_tentacles=False
        ),
        use_accurate_price_time_frame=True,
    )
