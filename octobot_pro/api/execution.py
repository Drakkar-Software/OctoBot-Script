import octobot_pro.internal.logging_util as logging_util
import octobot_pro.internal.runners as runners


async def run(backtesting_data, update_func, strategy_config,
              enable_logs=False, enable_storage=False):
    if enable_logs:
        logging_util.load_logging_config()
    return await runners.run(
        backtesting_data, update_func, strategy_config,
        enable_logs=enable_logs, enable_storage=enable_storage
    )
