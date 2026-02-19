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

import octobot.api as octobot_api
import octobot_backtesting.api as backtesting_api
import octobot_commons.constants as commons_constants
import octobot_commons.enums as commons_enums
import octobot_commons.logging as logging

import octobot_script.model as models
import octobot_script.internal.backtester_trading_mode as backtester_trading_mode
import octobot_script.internal.octobot_mocks as octobot_mocks


async def run(backtesting_data, strategy_config,
              enable_logs=False, enable_storage=False,
              strategy_func=None, initialize_func=None,
              tentacles_config=None, profile_id=None):
    backtest_result = models.BacktestResult(backtesting_data, strategy_config)
    registered_func = _build_script(strategy_func, initialize_func)
    _register_script(registered_func, strategy_config)
    run_tentacles_config = _resolve_run_tentacles_config(
        backtesting_data,
        strategy_func,
        tentacles_config,
        profile_id,
    )
    independent_backtesting = octobot_api.create_independent_backtesting(
        backtesting_data.config,
        run_tentacles_config,
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


def _resolve_run_tentacles_config(backtesting_data, strategy_func, tentacles_config, profile_id):
    activate_strategy_tentacles = strategy_func is not None
    if tentacles_config is None and profile_id is None:
        run_tentacles_config = backtesting_data.tentacles_config
        octobot_mocks.force_tentacles_config_activation(
            run_tentacles_config,
            activate_strategy_tentacles=activate_strategy_tentacles,
        )
        return run_tentacles_config
    return octobot_mocks.get_tentacles_config(
        tentacles_config,
        profile_id,
        activate_strategy_tentacles=activate_strategy_tentacles,
    )


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
    backtest_result.bot_id = independent_backtesting.octobot_backtesting.bot_id


def _build_script(strategy_func, initialize_func):
    """
    Compose strategy_func and initialize_func into a single
    async callable that the backtesting engine will invoke on every candle.

    Execution order per candle:
      1. initialize_func(ctx)  => only on the very first candle tick
      2. strategy_func(ctx)    => always (signal computation)
    """
    logger = logging.get_logger("Script Runner")
    initialized = [False]  # mutable container so the closure can mutate it

    async def _combined(ctx):
        if initialize_func is not None and not initialized[0]:
            try:
                await initialize_func(ctx)
            except Exception as err:
                logger.exception(err, True, f"Failed to execute initialization function: {err}")
            finally:
                initialized[0] = True
        try:
            if strategy_func is not None:
                await strategy_func(ctx)
        except Exception as err:
            logger.exception(err, True, f"Failed to execute strategy function: {err}")
    return _combined


def _register_script(script_func, strategy_config):
    def _local_import_scripts(self, *args):
        self._live_script = script_func
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
    backtester_trading_mode.BacktesterTradingMode._import_scripts = _local_import_scripts
