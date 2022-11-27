import asyncio
import tulipy
import octobot_backtester


async def ema_test():
    class Strategy(octobot_backtester.Strategy):
        async def update(self, ctx):
            rsi_v = tulipy.rsi(octobot_backtester.Close(ctx), period=self.config["period"])
            if rsi_v[-1] < self.config["buy_limit"]:
                await octobot_backtester.market(ctx, "buy", amount="10%",
                                                stop_loss_offset="-5%", take_profit_offset="5%")

    # data = await octobot_backtester.historical_data("BTC/USDT", timeframe="1d")
    data = "ExchangeHistoryDataCollector_1669309672.7815995.data"
    config = {
        "period": 10,
        "buy_limit": 30,
    }
    res = await octobot_backtester.run(data, Strategy, config)
    print(res.describe())


asyncio.run(ema_test())
