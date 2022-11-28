import asyncio
import tulipy
import octobot_backtester


async def ema_test():
    enable_logs = False
    async def update(ctx):
        close = await octobot_backtester.Close(ctx)
        if len(close) <= ctx.tentacle.trading_config["period"]:
            return
        rsi_v = tulipy.rsi(close, period=ctx.tentacle.trading_config["period"])
        if rsi_v[-1] < ctx.tentacle.trading_config["buy_limit"]:
            await octobot_backtester.market(ctx, "buy", amount="10%",
                                            stop_loss_offset="-5%", take_profit_offset="5%")
    if enable_logs:
        octobot_backtester.load_logging_config()
    # data = await octobot_backtester.historical_data("BTC/USDT", timeframe="1d")
    data = "ExchangeHistoryDataCollector_1669309672.7815995.data"
    config = {
        "period": 10,
        "buy_limit": 20,
    }
    res = await octobot_backtester.run(data, update, config, enable_logs=enable_logs)
    print(res.describe())
    print(await res.report())


asyncio.run(ema_test())
