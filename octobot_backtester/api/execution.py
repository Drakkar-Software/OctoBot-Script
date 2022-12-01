import octobot.api as octobot_api
import octobot_tentacles_manager.loaders as loaders
import octobot_backtesting.api as backtesting_api
import octobot_commons.constants as commons_constants
import octobot_commons.enums as commons_enums

import octobot_backtester.model as models


async def run(backtesting_data, update_func, strategy_config,
              enable_logs=False, enable_storage=False):
    # 1. load importers and reset cache indexes
    # 2. set candle managers

    backtest_result = models.BacktestResult(backtesting_data, strategy_config)
    if enable_logs:
        models.load_logging_config()

    loaders.reload_tentacle_by_tentacle_class()
    _register_strategy(update_func, strategy_config)
    independent_backtesting = octobot_api.create_independent_backtesting(
        backtesting_data.config,
        backtesting_data.tentacles_config,
        backtesting_data.data_files,
        run_on_common_part_only=True,
        start_timestamp=None,
        end_timestamp=None,
        enable_logs=enable_logs,
        stop_when_finished=False,
        run_on_all_available_time_frames=True,
        enforce_total_databases_max_size_after_run=False,
        enable_storage=enable_storage,
        backtesting_data=backtesting_data,
    )
    await octobot_api.initialize_and_run_independent_backtesting(independent_backtesting)
    await independent_backtesting.join_backtesting_updater(None)
    await _gather_results(independent_backtesting, backtest_result)
    await octobot_api.stop_independent_backtesting(independent_backtesting)
    return backtest_result


async def _gather_results(independent_backtesting, backtest_result):
    backtest_result.independent_backtesting = independent_backtesting
    backtest_result.duration = backtesting_api.get_backtesting_duration(
        independent_backtesting.octobot_backtesting.backtesting
    )
    backtest_result.candles_count = sum(
        candle_manager.get_preloaded_symbol_candles_count()
        for candle_manager in backtest_result.backtesting_data.preloaded_candle_managers.values()
    )
    backtest_result.report = await independent_backtesting.get_dict_formatted_report()


def _register_strategy(update_func, strategy_config):
    def _local_import_scripts(self, *args):
        self._live_script = update_func
        original_reload_config = self.reload_config

        async def _local_reload_config(*args, **kwargs):
            await original_reload_config(*args, **kwargs)
            updated_config = {
                commons_constants.CONFIG_ACTIVATION_TOPICS.replace(" ", "_"):
                    commons_enums.ActivationTopics.FULL_CANDLES.value
            }
            updated_config.update(strategy_config)
            self.trading_config.update(updated_config)
        self.reload_config = _local_reload_config

    import tentacles.Trading.Mode.scripted_trading_mode as scripted_trading_mode
    scripted_trading_mode.ScriptedTradingMode._import_scripts = _local_import_scripts
