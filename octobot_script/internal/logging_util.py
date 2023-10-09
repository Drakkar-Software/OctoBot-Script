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

import logging
import logging.config as config
import os.path

import octobot.logger
import octobot_script.internal.octobot_mocks as octobot_mocks


def load_logging_config(config_file="logging_config.ini"):
    if octobot.logger.BOT_CHANNEL_LOGGER is not None:
        # logs already initialized
        return
    logs_folder = "logs"
    if not os.path.exists(logs_folder):
        os.mkdir(logs_folder)
    try:
        config.fileConfig(config_file)
    except KeyError:
        logging_config = os.path.join(octobot_mocks.get_module_install_path(), "config", config_file)
        config.fileConfig(logging_config)
    octobot.logger.init_bot_channel_logger()


def enable_base_logger():
    logging.basicConfig(
        level=logging.DEBUG,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="%(asctime)s %(levelname)-8s %(name)-20s %(message)s"
    )

