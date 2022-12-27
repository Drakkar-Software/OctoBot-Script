import asyncio
import tulipy    # Can be any TA library.
import octobot_pro as op


async def rsi_test():
    async def strategy(ctx):
        # Will be called at each candle.
        if run_data["entries"] is None:
            # Compute entries only once per backtest.
            closes = await op.Close(ctx, max_history=True)
            times = await op.Time(ctx, max_history=True, use_close_time=True)
            rsi_v = tulipy.rsi(closes, period=ctx.tentacle.trading_config["period"])
            delta = len(closes) - len(rsi_v)
            # Populate entries with timestamps of candles where RSI is
            # bellow the "rsi_value_buy_threshold" configuration.
            run_data["entries"] = {
                times[index + delta]
                for index, rsi_val in enumerate(rsi_v)
                if rsi_val < ctx.tentacle.trading_config["rsi_value_buy_threshold"]
            }
            await op.plot_indicator(ctx, "RSI", times[delta:], rsi_v, run_data["entries"])
        if op.current_live_time(ctx) in run_data["entries"]:
            # Uses pre-computed entries times to enter positions when relevant.
            # Also, instantly set take profits and stop losses.
            # Position exists could also be set separately.
            await op.market(ctx, "buy", amount="10%", stop_loss_offset="-15%", take_profit_offset="25%")

    # Configuration that will be passed to each run.
    # It will be accessible under "ctx.tentacle.trading_config".
    config = {
        "period": 10,
        "rsi_value_buy_threshold": 28,
    }

    # Read and cache candle data to make subsequent backtesting runs faster.
    data = await op.get_data("BTC/USDT", "1d", start_timestamp=1505606400)
    run_data = {
        "entries": None,
    }
    # Run a backtest using the above data, strategy and configuration.
    res = await op.run(data, strategy, config)
    print(res.describe())
    # Generate and open report including indicators plots
    await res.plot(show=True)
    # Stop data to release local databases.
    await data.stop()


# Call the execution of the script inside "asyncio.run" as
# OctoBot-Pro runs using the python asyncio framework.
asyncio.run(rsi_test())
