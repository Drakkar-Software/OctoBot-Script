#  This file is part of OctoBot-Script (https://github.com/Drakkar-Software/OctoBot-Script)
#  Copyright (c) 2023 Drakkar-Software, All rights reserved.
#
#  OctoBot is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  OctoBot is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public
#  License along with OctoBot-Script. If not, see <https://www.gnu.org/licenses/>.

import pytest
import mock

import octobot_script as obs
import octobot_script.internal.logging_util as logging_util
import octobot_script.internal.runners as runners


# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_run():
    with mock.patch.object(logging_util, "load_logging_config", mock.Mock()) as load_logging_config_mock, \
         mock.patch.object(runners, "run", mock.AsyncMock(return_value="ret")) as run_mock:
        def up_func():
            pass
        assert await obs.run("backtesting_data", up_func, "strat_config") == "ret"
        load_logging_config_mock.assert_not_called()
        run_mock.assert_awaited_once_with("backtesting_data", up_func, "strat_config",
                                          enable_logs=False, enable_storage=True)
        load_logging_config_mock.reset_mock()
        run_mock.reset_mock()
        assert await obs.run("backtesting_data", up_func, "strat_config", enable_logs=True, enable_storage=False) \
               == "ret"
        load_logging_config_mock.assert_called_once()
        run_mock.assert_awaited_once_with("backtesting_data", up_func, "strat_config",
                                          enable_logs=True, enable_storage=False)
