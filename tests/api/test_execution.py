import pytest
import mock

import octobot_pro as op
import octobot_pro.internal.logging_util as logging_util
import octobot_pro.internal.runners as runners


# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_run():
    with mock.patch.object(logging_util, "load_logging_config", mock.Mock()) as load_logging_config_mock, \
         mock.patch.object(runners, "run", mock.AsyncMock(return_value="ret")) as run_mock:
        def up_func():
            pass
        assert await op.run("backtesting_data", up_func, "strat_config") == "ret"
        load_logging_config_mock.assert_not_called()
        run_mock.assert_awaited_once_with("backtesting_data", up_func, "strat_config",
                                          enable_logs=False, enable_storage=True)
        load_logging_config_mock.reset_mock()
        run_mock.reset_mock()
        assert await op.run("backtesting_data", up_func, "strat_config", enable_logs=True, enable_storage=False) \
               == "ret"
        load_logging_config_mock.assert_called_once()
        run_mock.assert_awaited_once_with("backtesting_data", up_func, "strat_config",
                                          enable_logs=True, enable_storage=False)
