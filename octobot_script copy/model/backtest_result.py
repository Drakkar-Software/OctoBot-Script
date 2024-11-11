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

import os
import octobot_script.model.backtest_plot as backtest_plot
import octobot_script.model.errors as errors
import octobot_commons.databases as commons_databases


class BacktestResult:
    def __init__(self, backtesting_data, strategy_config):
        self.backtesting_data = backtesting_data
        self.strategy_config = strategy_config
        self.independent_backtesting = None
        self.duration = None
        self.candles_count = None
        self.report = {}
        self.bot_id = None

    def describe(self):
        return f"[{round(self.duration, 3)}s / {self.candles_count} candles] profitability: {self.report['bot_report']['profitability']} " \
               f"market average: {self.report['bot_report']['market_average_profitability']} " \
               f"strategy_config: {self.strategy_config}"

    async def plot(self, report_file=None, show=False):
        if not commons_databases.RunDatabasesProvider.instance().is_storage_enabled(self.bot_id):
            raise errors.ParameterError("storage has to be enabled to plot backtesting data")
        plot_result = await self._get_plotted_result(report_file=report_file)
        if show:
            plot_result.show()
        return plot_result

    async def _get_plotted_result(self, report_file=None):
        run_db_id = commons_databases.RunDatabasesProvider.instance().get_run_databases_identifier(self.bot_id)
        plot = backtest_plot.BacktestPlot(
            self, run_db_id, report_file=report_file or self.get_default_plotted_report_file(run_db_id)
        )
        await plot.fill()
        return plot

    def get_default_plotted_report_file(self, run_db_id):
        return os.path.join(
            run_db_id.get_backtesting_run_folder(),
            backtest_plot.BacktestPlot.DEFAULT_REPORT_NAME
        )
