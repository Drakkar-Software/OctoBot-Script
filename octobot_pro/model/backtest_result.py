import json


class BacktestResult:
    def __init__(self, backtesting_data, strategy_config):
        self.backtesting_data = backtesting_data
        self.strategy_config = strategy_config
        self.independent_backtesting = None
        self.duration = None
        self.candles_count = None
        self.report = None

    def report(self):
        return json.dumps(
            self.report,
            indent=4
        )

    def describe(self):
        return f"[{round(self.duration, 3)}s / {self.candles_count} candles] profitability: {self.report['bot_report']['profitability']} " \
               f"market average: {self.report['bot_report']['market_average_profitability']} " \
               f"strategy_config: {self.strategy_config}"
