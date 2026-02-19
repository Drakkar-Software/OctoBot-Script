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
import html
import os
import re
import shutil
import time
import json

import octobot_commons.constants as commons_constants
import octobot_commons.display as display
import octobot_commons.logging as logging
import octobot_commons.timestamp_util as timestamp_util
import octobot.api as octobot_api
import octobot_tentacles_manager.api as tentacles_manager_api
import octobot_script.resources as resources
import octobot_script.internal.backtester_trading_mode as backtester_trading_mode
from octobot_script.model.backtest_report_server import BacktestReportServer


class BacktestPlot:
    DEFAULT_REPORT_NAME = "report.html"
    ADVANCED_TEMPLATE = os.path.join("dist", "index.html")
    DEFAULT_TEMPLATE = ADVANCED_TEMPLATE
    REPORT_DATA_FILENAME = "report_data.json"
    REPORT_META_FILENAME = "report_meta.json"
    REPORT_BUNDLE_FILENAME = "report.json"
    HISTORY_DIR = "backtesting"
    HISTORY_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
    GENERATED_TIME_FORMAT = "%Y-%m-%d at %H:%M:%S"
    SERVER_PORT = 5555
    SERVER_HOST = "localhost"
    SERVE_TIMEOUT = 300  # seconds — keep server alive for history browsing

    def __init__(self, backtest_result, run_db_identifier, report_file=None):
        self.backtest_result = backtest_result
        self.report_file = report_file
        self.run_db_identifier = run_db_identifier
        self.backtesting_analysis_settings = (
            self.default_backtesting_analysis_settings()
        )

    async def fill(self, template_file=None):
        template_name = template_file or self.DEFAULT_TEMPLATE
        template_data = await self._get_template_data()
        report_dir = os.path.dirname(os.path.abspath(self.report_file))
        shutil.copy2(
            resources.get_report_resource_path(template_name), self.report_file
        )
        meta = template_data["meta"]
        with open(
            os.path.join(report_dir, self.REPORT_DATA_FILENAME), "w", encoding="utf-8"
        ) as f:
            f.write(template_data["full_data"])
        with open(
            os.path.join(report_dir, self.REPORT_META_FILENAME), "w", encoding="utf-8"
        ) as f:
            json.dump(meta, f)
        bundle = {"meta": meta, "data": json.loads(template_data["full_data"])}
        with open(
            os.path.join(report_dir, self.REPORT_BUNDLE_FILENAME), "w", encoding="utf-8"
        ) as f:
            json.dump(bundle, f)
        self._save_history_entry(report_dir, template_data["full_data"], meta, bundle)

    def _save_history_entry(self, report_dir, data_str, meta, bundle):
        ts = time.strftime(self.HISTORY_TIMESTAMP_FORMAT)
        run_dir = os.path.join(report_dir, self.HISTORY_DIR, ts)
        os.makedirs(run_dir, exist_ok=True)
        with open(
            os.path.join(run_dir, self.REPORT_DATA_FILENAME), "w", encoding="utf-8"
        ) as f:
            f.write(data_str)
        with open(
            os.path.join(run_dir, self.REPORT_META_FILENAME), "w", encoding="utf-8"
        ) as f:
            json.dump(meta, f)
        with open(
            os.path.join(run_dir, self.REPORT_BUNDLE_FILENAME), "w", encoding="utf-8"
        ) as f:
            json.dump(bundle, f)

    def show(self):
        import octobot_script.internal.octobot_mocks as octobot_mocks

        report_dir = os.path.dirname(os.path.abspath(self.report_file))
        report_name = os.path.basename(self.report_file)
        runs_root_dir = os.path.dirname(report_dir)
        user_data_dir = octobot_mocks.get_module_appdir_path()
        print(f"Report: {self.report_file}")
        server = BacktestReportServer(
            report_file=self.report_file,
            report_dir=report_dir,
            report_name=report_name,
            runs_root_dir=runs_root_dir,
            server_host=self.SERVER_HOST,
            server_port=self.SERVER_PORT,
            serve_timeout=self.SERVE_TIMEOUT,
            history_dir=self.HISTORY_DIR,
            data_filename=self.REPORT_DATA_FILENAME,
            meta_filename=self.REPORT_META_FILENAME,
            bundle_filename=self.REPORT_BUNDLE_FILENAME,
        )
        server.user_data_dir = user_data_dir
        server.serve()

    async def _get_template_data(self):
        full_data, symbols, time_frames, exchanges = await self._get_full_data()
        summary = self._extract_summary_metrics(full_data)
        trading_mode = self._resolve_trading_mode_class()
        return {
            "full_data": full_data,
            "meta": {
                "title": f"{', '.join(symbols)}",
                "creation_time": timestamp_util.convert_timestamp_to_datetime(
                    time.time(), self.GENERATED_TIME_FORMAT, local_timezone=True
                ),
                "strategy_config": self.backtest_result.strategy_config,
                "symbols": symbols,
                "time_frames": time_frames,
                "exchanges": exchanges,
                "summary": summary,
                "trading_mode": trading_mode.get_name() if trading_mode else None,
            },
        }

    @staticmethod
    def _extract_summary_metrics(full_data):
        try:
            parsed = json.loads(full_data)
            sub_elements = parsed.get("data", {}).get("sub_elements", [])
            details = next(
                (
                    element
                    for element in sub_elements
                    if element.get("name") == "backtesting-details"
                    and element.get("type") == "value"
                ),
                None,
            )
            values = details.get("data", {}).get("elements", []) if details else []
            metrics = {}
            for element in values:
                title = element.get("title")
                value = element.get("value")
                if title and value is not None:
                    metrics[str(title)] = str(value)
                metric_html = element.get("html")
                if metric_html:
                    metrics.update(BacktestPlot._extract_metrics_from_html(metric_html))

            def _find_metric(candidates):
                for key, value in metrics.items():
                    lowered = key.lower()
                    if any(candidate in lowered for candidate in candidates):
                        return value
                return None

            return {
                "profitability": _find_metric(
                    ("usdt gains", "profitability", "profit", "roi", "return")
                ),
                "portfolio": _find_metric(
                    ("end portfolio usdt value", "end portfolio", "portfolio")
                ),
                "metrics": metrics,
            }
        except Exception:
            return {"profitability": None, "portfolio": None, "metrics": {}}

    @staticmethod
    def _extract_metrics_from_html(metric_html):
        metrics = {}
        matches = re.findall(
            r"backtesting-run-container-values-label[^>]*>\s*(.*?)\s*</div>\s*"
            r"<div[^>]*backtesting-run-container-values-value[^>]*>\s*(.*?)\s*</div>",
            metric_html,
            flags=re.IGNORECASE | re.DOTALL,
        )
        for raw_label, raw_value in matches:
            label = BacktestPlot._html_to_text(raw_label)
            value = BacktestPlot._html_to_text(raw_value)
            if label and value:
                metrics[label] = value
        return metrics

    @staticmethod
    def _html_to_text(content):
        no_tags = re.sub(r"<[^>]+>", " ", content or "")
        return re.sub(r"\s+", " ", html.unescape(no_tags)).strip()

    async def _get_full_data(self):
        # tentacles not available during first install
        import tentacles.Meta.Keywords.scripting_library as scripting_library

        logger = logging.get_logger(self.__class__.__name__)
        elements = display.display_translator_factory()
        trading_mode = self._resolve_trading_mode_class()
        symbols = []
        time_frames = []
        exchanges = []
        for (
            exchange,
            available_symbols,
        ) in octobot_api.get_independent_backtesting_symbols_by_exchanges(
            self.backtest_result.independent_backtesting
        ).items():
            exchanges.append(exchange)
            for symbol in available_symbols:
                symbol = str(symbol)
                symbols.append(symbol)
                for time_frame in octobot_api.get_independent_backtesting_config(
                    self.backtest_result.independent_backtesting
                )[commons_constants.CONFIG_TIME_FRAME]:
                    time_frames.append(time_frame.value)
                    await elements.fill_from_database(
                        trading_mode,
                        self.run_db_identifier,
                        exchange,
                        symbol,
                        time_frame.value,
                        None,
                        with_inputs=False,
                    )
                    ctx = scripting_library.Context.minimal(
                        trading_mode,
                        logger,
                        exchange,
                        symbol,
                        self.run_db_identifier.backtesting_id,
                        self.run_db_identifier.optimizer_id,
                        self.run_db_identifier.optimization_campaign_name,
                        self.backtesting_analysis_settings,
                    )
                    try:
                        elements.add_parts_from_other(
                            await scripting_library.default_backtesting_analysis_script(
                                ctx
                            )
                        )
                    except Exception as err:
                        logger.error(
                            f"Failed to build advanced analysis for {exchange} {symbol} {time_frame.value}: {err}"
                        )
        return json.dumps(elements.to_json()), symbols, time_frames, exchanges

    def _resolve_trading_mode_class(self):
        trading_mode_name = getattr(self.run_db_identifier, "tentacle_class", None)
        if trading_mode_name:
            try:
                if (
                    trading_mode_name
                    == backtester_trading_mode.BacktesterTradingMode.__name__
                ):
                    return backtester_trading_mode.BacktesterTradingMode
                resolved = tentacles_manager_api.get_tentacle_class_from_string(
                    trading_mode_name
                )
                if resolved is not None:
                    return resolved
            except Exception:
                pass
        return backtester_trading_mode.BacktesterTradingMode

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
