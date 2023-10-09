# OctoBot-Script [0.0.12](https://github.com/Drakkar-Software/OctoBot-Script/tree/master/CHANGELOG.md)
[![PyPI](https://img.shields.io/pypi/v/OctoBot-Script.svg?logo=pypi)](https://pypi.python.org/pypi/OctoBot-Script/)
[![Downloads](https://static.pepy.tech/badge/OctoBot-Script/month)](https://pepy.tech/project/OctoBot-Script)
[![Dockerhub](https://img.shields.io/docker/pulls/drakkarsoftware/OctoBot-Script.svg?logo=docker)](https://hub.docker.com/r/drakkarsoftware/OctoBot-Script)
[![Github-Action-CI](https://github.com/Drakkar-Software/OctoBot-Script/workflows/OctoBot-Script-CI/badge.svg)](https://github.com/Drakkar-Software/OctoBot-Script/actions)

## OctoBot-Script Community
[![Telegram Chat](https://img.shields.io/badge/telegram-chat-green.svg?logo=telegram&label=Telegram)](https://octobot.click/readme-telegram-OctoBot-Script)
[![Discord](https://img.shields.io/discord/530629985661222912.svg?logo=discord&label=Discord)](https://octobot.click/gh-discord-OctoBot-Script)
[![Twitter](https://img.shields.io/twitter/follow/DrakkarsOctobot.svg?label=twitter&style=social)](https://octobot.click/gh-twitter-OctoBot-Script)


## OctoBot Script is the backtesting framework using the OctoBot Ecosystem

> OctoBot Script is in early alpha version

Documentation available at [https://pro.octobot.info/](https://octobot.click/Xzae1a6)


## Install OctoBot Script from pip

> OctoBot Script requires **Python 3.10**

``` {.sourceCode .bash}
python3 -m pip install OctoBot wheel
python3 -m pip install octobot-script
```

## Example of a backtesting script

### Script
``` python
import asyncio
import tulipy    # Can be any TA library.
import octobot_script as obs


async def rsi_test():
    async def strategy(ctx):
        # Will be called at each candle.
        if run_data["entries"] is None:
            # Compute entries only once per backtest.
            closes = await obs.Close(ctx, max_history=True)
            times = await obs.Time(ctx, max_history=True, use_close_time=True)
            rsi_v = tulipy.rsi(closes, period=ctx.tentacle.trading_config["period"])
            delta = len(closes) - len(rsi_v)
            # Populate entries with timestamps of candles where RSI is
            # bellow the "rsi_value_buy_threshold" configuration.
            run_data["entries"] = {
                times[index + delta]
                for index, rsi_val in enumerate(rsi_v)
                if rsi_val < ctx.tentacle.trading_config["rsi_value_buy_threshold"]
            }
            await obs.plot_indicator(ctx, "RSI", times[delta:], rsi_v, run_data["entries"])
        if obs.current_live_time(ctx) in run_data["entries"]:
            # Uses pre-computed entries times to enter positions when relevant.
            # Also, instantly set take profits and stop losses.
            # Position exists could also be set separately.
            await obs.market(ctx, "buy", amount="10%", stop_loss_offset="-15%", take_profit_offset="25%")

    # Configuration that will be passed to each run.
    # It will be accessible under "ctx.tentacle.trading_config".
    config = {
        "period": 10,
        "rsi_value_buy_threshold": 28,
    }

    # Read and cache candle data to make subsequent backtesting runs faster.
    data = await obs.get_data("BTC/USDT", "1d", start_timestamp=1505606400)
    run_data = {
        "entries": None,
    }
    # Run a backtest using the above data, strategy and configuration.
    res = await obs.run(data, strategy, config)
    print(res.describe())
    # Generate and open report including indicators plots 
    await res.plot(show=True)
    # Stop data to release local databases.
    await data.stop()


# Call the execution of the script inside "asyncio.run" as
# OctoBot-Script runs using the python asyncio framework.
asyncio.run(rsi_test())
```

### Generated report
![report-p1](https://raw.githubusercontent.com/Drakkar-Software/OctoBot-Script/assets/images/report_1.jpg)

### Join the community
We recently created a telegram channel dedicated to OctoBot Script.

[![Telegram News](https://img.shields.io/static/v1?label=Telegram%20chat&message=Join&logo=telegram&&color=007bff&style=for-the-badge)](https://octobot.click/readme-telegram-OctoBot-Pro)
