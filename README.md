# Octobot-Pro [0.0.1](https://github.com/Drakkar-Software/OctoBot-Pro/tree/master/CHANGELOG.md)
[![PyPI](https://img.shields.io/pypi/v/octobot-pro.svg)](https://pypi.python.org/pypi/octobot-pro/)
[![Downloads](https://pepy.tech/badge/octobot-pro/month)](https://pepy.tech/project/octobot-pro)
[![Github-Action-CI](https://github.com/Drakkar-Software/octobot-pro/workflows/octobot-pro-CI/badge.svg)](https://github.com/Drakkar-Software/octobot-pro/actions)

## OctoBot Pro is the backtesting framework using the OctoBot Ecosystem

> OctoBot Pro is in early alpha version

## Install OctoBot Pro from pip

``` {.sourceCode .bash}
$ python3 -m pip install octobot-pro
```

## Example of a backtesting script

``` python
import asyncio
import tulipy    # Can be any TA library.
import octobot_pro as op


async def rsi_test():
    # read and cache candle data to make subsequent backtesting runs faster.
    data = await op.get_data("BTC/USDT", "1d", start_timestamp=1505606400)
    run_data = {
        "entries": None,
    }

    async def strategy(ctx):
        # Will be called at each candle.
        if run_data["entries"] is None:
            # Compute entries only once per backtest.
            closes = await op.Close(ctx, max_history=True)
            times = await op.Time(ctx, max_history=True, use_close_time=True)
            rsi_v = tulipy.rsi(closes, period=ctx.tentacle.trading_config["period"])
            delta = len(closes) - len(rsi_v) + 1
            # Populate entries with timestamps of candles where RSI is
            # bellow the "buy_limit" configuration.
            run_data["entries"] = {
                times[index + delta]
                for index, rsi_val in enumerate(rsi_v)
                if rsi_val < ctx.tentacle.trading_config["buy_limit"]
            }
        if op.current_live_time(ctx) in run_data["entries"]:
            # Uses pre-computed entries times to enter positions when relevant.
            # Also instantly set take profits and stop losses.
            # Position exists could also be set separately.
            await op.market(ctx, "buy", amount="10%", stop_loss_offset="-5%", take_profit_offset="5%")

    # Configuration that will be passed to each run
    # It will be accessible under "ctx.tentacle.trading_config"
    config = {
        "period": 10,
        "buy_limit": 30,
    }

    # Run a backtest using the above data, strategy and configuration.
    # When looping, subsequent runs will be faster as many elements are cached.
    res = await op.run(data, strategy, config)
    print(res.describe())

    # stop data to release local databases.
    await data.stop()


# Call the execution of the script inside "asyncio.run" as
# OctoBot-Pro runs using the python asyncio framework.
asyncio.run(rsi_test())
```
