import asyncio
import octobot_script as obs


async def start_profile():
    config = {}
    profile_id = "dip_analyser"

    # Read and cache candle data to make subsequent backtesting runs faster.
    data = await obs.get_data(
        "BTC/USDT",
        "1d",
        start_timestamp=1505606400,
        profile_id=profile_id,
    )
    # Run a backtest using the above data, strategy and configuration.
    res = await obs.run(data, config, profile_id=profile_id)
    print(res.describe())
    # Generate and open report including indicators plots
    await obs.generate_and_show_report(res)
    # Stop data to release local databases.
    await data.stop()


# Call the execution of the script inside "asyncio.run" as
# OctoBot-Script runs using the python asyncio framework.
asyncio.run(start_profile())
