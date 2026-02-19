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

import octobot_script.internal.logging_util as logging_util
import octobot_script.internal.runners as runners


async def run(backtesting_data, strategy_config,
              enable_logs=False, enable_storage=True,
              strategy_func=None, initialize_func=None,
              tentacles_config=None, profile_id=None):
    if tentacles_config is not None and profile_id is not None:
        raise ValueError("Only one of tentacles_config or profile_id can be provided.")
    if enable_logs:
        logging_util.load_logging_config()
    return await runners.run(
        backtesting_data, strategy_config,
        enable_logs=enable_logs, enable_storage=enable_storage,
        strategy_func=strategy_func, initialize_func=initialize_func,
        tentacles_config=tentacles_config, profile_id=profile_id,
    )
