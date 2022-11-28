import json

class BacktestResult:
    def __init__(self, data_files, strategy_config):
        self.data_files = data_files
        self.strategy_config = strategy_config
        self.independent_backtesting = None
        self.duration = None

    async def report(self):
        return json.dumps(
            await self.independent_backtesting.get_dict_formatted_report(),
            indent=4
        )

    def describe(self):
        return f"{BacktestResult.__class__.__name__} duration: {round(self.duration, 3)}s " \
               f"strategy_config: {self.strategy_config}"
