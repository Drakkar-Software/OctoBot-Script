import octobot.api as octobot_api
import octobot_backtester.internal.octobot_mocks as octobot_mocks
import octobot_tentacles_manager.loaders as loaders
import octobot_backtester.model as models
import octobot_backtesting.api as backtesting_api
import octobot_commons.constants as commons_constants
import octobot_commons.enums as commons_enums


async def run(data_files, update_func, strategy_config, enable_logs=False, all_timeframes=True):
    backtest_result = models.BacktestResult(data_files, strategy_config)

    loaders.reload_tentacle_by_tentacle_class()
    _register_strategy(update_func, strategy_config)
    independent_backtesting = octobot_api.create_independent_backtesting(
        octobot_mocks.get_config(),
        octobot_mocks.get_tentacles_config(),
        [data_files],
        run_on_common_part_only=True,
        start_timestamp=None,
        end_timestamp=None,
        enable_logs=True,
        stop_when_finished=False,
        run_on_all_available_time_frames=True,
        enforce_total_databases_max_size_after_run=False,
    )
    await octobot_api.initialize_and_run_independent_backtesting(independent_backtesting)
    await independent_backtesting.join_backtesting_updater(None)
    # await octobot_api.stop_independent_backtesting(independent_backtesting)
    backtest_result.independent_backtesting = independent_backtesting
    backtest_result.duration = backtesting_api.get_backtesting_duration(
        independent_backtesting.octobot_backtesting.backtesting
    )
    return backtest_result


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
