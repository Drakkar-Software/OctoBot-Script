import webbrowser
import jinja2
import json

import octobot_pro.resources as resources
import octobot_commons.constants as commons_constants
import octobot_commons.display as display
import octobot_commons.logging as logging


class BacktestPlot:
    DEFAULT_REPORT_NAME = "report.html"
    DEFAULT_TEMPLATE = "default_report_template.html"
    JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(
        resources.get_report_resource_path(None)
    ))

    def __init__(self, backtest_result, run_db_identifier, report_file=None):
        self.backtest_result = backtest_result
        self.report_file = report_file
        self.run_db_identifier = run_db_identifier
        self.backtesting_analysis_settings = self.default_backtesting_analysis_settings()

    async def fill(self, template_file=None):
        template = self.JINJA_ENVIRONMENT.get_template(template_file or self.DEFAULT_TEMPLATE)
        template_data = await self._get_template_data()
        with open(self.report_file, "w") as report:
            report.write(template.render(template_data))

    def show(self):
        return webbrowser.open(self.report_file)

    async def _get_template_data(self):
        full_data, symbols, time_frames, exchanges = await self._get_full_data()
        return {
            "FULL_DATA": full_data,
            "title": f"{', '.join(symbols)}",
            "top_title": f"{', '.join(symbols)} on {', '.join(time_frames)} from "
                         f"{', '.join([e.capitalize() for e in exchanges])}",
            "middle_title": "Portfolio value",
            "bottom_title": "Details",
            "strategy_config": self.backtest_result.strategy_config
        }

    async def _get_full_data(self):
        # tentacles not available during first install
        import tentacles.Trading.Mode as trading_modes
        import tentacles.Meta.Keywords.scripting_library as scripting_library
        elements = display.display_translator_factory()
        trading_mode = trading_modes.ScriptedTradingMode
        symbols = []
        time_frames = []
        exchanges = []
        for exchange, available_symbols in self.backtest_result.independent_backtesting.octobot_backtesting. \
             symbols_to_create_exchange_classes.items():
            exchanges.append(exchange)
            for symbol in available_symbols:
                symbol = str(symbol)
                symbols.append(symbol)
                for time_frame in self.backtest_result.independent_backtesting.octobot_backtesting.backtesting_config[
                    commons_constants.CONFIG_TIME_FRAME
                ]:
                    time_frames.append(time_frame.value)
                    await elements.fill_from_database(
                        trading_mode, self.run_db_identifier, exchange, symbol, time_frame.value,
                        None, with_inputs=False
                    )
                    ctx = scripting_library.Context.minimal(
                        trading_mode, logging.get_logger(self.__class__.__name__), exchange, symbol,
                        self.run_db_identifier.backtesting_id, self.run_db_identifier.optimizer_id,
                        self.run_db_identifier.optimization_campaign_name, self.backtesting_analysis_settings)
                    elements.add_parts_from_other(await scripting_library.default_backtesting_analysis_script(ctx))
        return json.dumps(elements.to_json()), symbols, time_frames, exchanges

    def default_backtesting_analysis_settings(self):
        return {
            "display_backtest_details": True,
            "display_trades_and_positions": True,
            "plot_best_case_growth_on_backtesting_chart": False,
            "plot_funding_fees_on_backtesting_chart": False,
            "plot_hist_portfolio_on_backtesting_chart": True,
            "plot_pnl_on_backtesting_chart": False,
            "plot_pnl_on_main_chart": False,
            "plot_trade_gains_on_backtesting_chart": False,
            "plot_trade_gains_on_main_chart": False,
            "plot_win_rate_on_backtesting_chart": False,
            "plot_wins_and_losses_count_on_backtesting_chart": False,
            "display_backtest_details_general": False,
            "display_backtest_details_performances": True,
            "display_backtest_details_details": False,
            "display_backtest_details_strategy_settings": False,
        }
