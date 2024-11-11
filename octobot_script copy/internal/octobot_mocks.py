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

import os
import json
import appdirs

import octobot_script
import octobot_script.constants as constants
import octobot_script.internal.backtester_trading_mode
import octobot_commons.constants as commons_constants
import octobot_tentacles_manager.api as octobot_tentacles_manager_api
import octobot_tentacles_manager.constants as octobot_tentacles_manager_constants
import octobot.configuration_manager as octobot_configuration_manager


def get_tentacles_config():
    # use tentacles config from user appdirs as it is kept up to date at each tentacle packages install
    ref_tentacles_config_path = os.path.join(
        get_module_appdir_path(),
        octobot_tentacles_manager_constants.USER_REFERENCE_TENTACLE_CONFIG_PATH,
        commons_constants.CONFIG_TENTACLES_FILE
    )
    tentacles_setup_config = octobot_tentacles_manager_api.get_tentacles_setup_config(ref_tentacles_config_path)
    # activate OctoBot-Script required tentacles
    _force_tentacles_config_activation(tentacles_setup_config)
    return tentacles_setup_config


def get_config():
    with open(get_module_config_path("config_mock.json")) as f:
        return json.load(f)


def get_module_install_path():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_module_config_path(file_name):
    return os.path.join(get_module_install_path(), constants.CONFIG_PATH, file_name)


def get_module_appdir_path():
    dirs = appdirs.AppDirs(octobot_script.PROJECT_NAME, octobot_script.AUTHOR, octobot_script.VERSION)
    return dirs.user_data_dir


def get_internal_import_path():
    return os.path.join(get_module_appdir_path(), constants.ADDITIONAL_IMPORT_PATH)


def get_tentacles_path():
    return os.path.join(get_internal_import_path(), octobot_tentacles_manager_constants.TENTACLES_PATH)


def get_imported_tentacles_path():
    import tentacles
    return os.path.dirname(os.path.abspath(tentacles.__file__))


def get_public_tentacles_urls():
    return [
        octobot_configuration_manager.get_default_tentacles_url()
    ]


def _force_tentacles_config_activation(tentacles_setup_config):
    import tentacles.Evaluator
    forced_tentacles = {
        octobot_tentacles_manager_constants.TENTACLES_EVALUATOR_PATH: {
            tentacles.Evaluator.BlankStrategyEvaluator.get_name(): True
        },
        octobot_tentacles_manager_constants.TENTACLES_TRADING_PATH: {
            octobot_script.internal.backtester_trading_mode.BacktesterTradingMode.get_name(): True
        }
    }
    for topic, activations in forced_tentacles.items():
        for tentacle, activated in activations.items():
            tentacles_setup_config.tentacles_activation[topic][tentacle] = activated
