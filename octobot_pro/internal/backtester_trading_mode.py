import octobot_trading.modes as modes
import octobot_trading.enums as trading_enums


class BacktesterTradingMode(modes.AbstractScriptedTradingMode):

    def __init__(self, config, exchange_manager):
        super().__init__(config, exchange_manager)
        self._import_scripts()

    def _import_scripts(self):
        pass

    @classmethod
    def get_supported_exchange_types(cls) -> list:
        """
        :return: The list of supported exchange types
        """
        return [
            trading_enums.ExchangeTypes.SPOT,
            trading_enums.ExchangeTypes.FUTURE,
            trading_enums.ExchangeTypes.MARGIN,
        ]
