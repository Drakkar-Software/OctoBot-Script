import octobot.api as octobot_api
import octobot_backtester.internal.octobot_mocks as octobot_mocks
import octobot_tentacles_manager.loaders as loaders


async def run(data_files, strategy_class, strategy_config, enable_logs=False, all_timeframes=True):
    # todo: register strategy_class as trading mode and run on all available time frames

    loaders.reload_tentacle_by_tentacle_class()
    independent_backtesting = octobot_api.create_independent_backtesting(
        octobot_mocks.get_config(),
        octobot_mocks.get_tentacles_config(),
        [data_files],
        run_on_common_part_only=True,
        start_timestamp=None,
        end_timestamp=None,
        enable_logs=enable_logs,
        stop_when_finished=True,
        run_on_all_available_time_frames=True
    )
    await octobot_api.initialize_and_run_independent_backtesting(independent_backtesting)
    await octobot_api.stop_independent_backtesting(independent_backtesting)
