import asyncio
import tulipy
import time
import octobot_pro as op


async def rsi_test():
    data = await op.get_data("BTC/USDT", "1d", start_timestamp=1505606400)

    run_data = {
        "entries": None,
    }

    async def run_test():
        async def _iterations_update(ctx):
            if op.current_live_time(ctx) != await op.current_candle_time(
                    ctx, use_close_time=True):
                print("missing candle")
                return
            close = await op.Close(ctx)
            if len(close) <= ctx.tentacle.trading_config["period"]:
                return
            rsi_v = tulipy.rsi(close, period=ctx.tentacle.trading_config["period"])
            if rsi_v[-1] < ctx.tentacle.trading_config["buy_limit"]:
                await op.market(ctx, "buy", amount="10%",
                                                stop_loss_offset="-5%", take_profit_offset="5%")

        async def _pre_compute_update(ctx):
            if run_data["entries"] is None:
                closes = await op.Close(ctx, max_history=True)
                times = await op.Time(ctx, max_history=True, use_close_time=True)
                rsi_v = tulipy.rsi(closes, period=ctx.tentacle.trading_config["period"])
                delta = len(closes) - len(rsi_v) + 1
                run_data["entries"] = {
                    times[index + delta]
                    for index, rsi_val in enumerate(rsi_v)
                    if rsi_val < ctx.tentacle.trading_config["buy_limit"]
                }
            if op.current_live_time(ctx) in run_data["entries"]:
                await op.market(ctx, "buy", amount="10%",
                                                stop_loss_offset="-5%", take_profit_offset="5%")
        config = {
            "period": 10,
            "buy_limit": 30,
        }
        res = await op.run(data, _pre_compute_update, config,
                                           enable_logs=False, enable_storage=False)
        print(res.describe())
        # res = await op.run(data, _iterations_update, config, enable_logs=False, enable_storage=False)
        # print(res.describe())

    RUNS = 1
    t0 = time.time()
    for _ in range(RUNS):
        await run_test()
    print(f"total duration: {round(time.time()-t0, 3)}")
    await data.stop()



asyncio.run(rsi_test())
