import octobot_backtesting.api as backtesting_api
import octobot_commons.symbols as commons_symbols
import octobot_commons.enums as commons_enums
import octobot_trading.enums as trading_enums
import octobot_pro.internal.octobot_mocks as octobot_mocks


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
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp)
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
