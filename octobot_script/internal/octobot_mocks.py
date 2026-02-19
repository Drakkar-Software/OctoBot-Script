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
import octobot_commons.logging as commons_logging
import octobot_commons.profiles as commons_profiles
import octobot_commons.tentacles_management.class_inspector as class_inspector
import octobot_tentacles_manager.api as octobot_tentacles_manager_api
import octobot_tentacles_manager.constants as octobot_tentacles_manager_constants
import octobot.configuration_manager as octobot_configuration_manager
import octobot_services.service_feeds as services_feeds
import octobot_services.api as services_api

LOGGER = commons_logging.get_logger("OctoBot-Script Tentacles")


def get_tentacles_config(forced_tentacles_by_topic=None, profile_id=None, activate_strategy_tentacles=False):
    _validate_tentacles_config_source(forced_tentacles_by_topic, profile_id)
    # use tentacles config from user appdirs as it is kept up to date at each tentacle packages install
    tentacles_setup_config = octobot_tentacles_manager_api.get_tentacles_setup_config(
        _get_tentacles_config_path(profile_id)
    )
    if not tentacles_setup_config.is_successfully_loaded:
        # reference config not available (tentacles not yet installed via CLI),
        # populate from currently imported tentacles
        octobot_tentacles_manager_api.fill_with_installed_tentacles(
            tentacles_setup_config,
            tentacles_folder=get_imported_tentacles_path()
        )
    # activate OctoBot-Script required tentacles
    _force_tentacles_config_activation(
        tentacles_setup_config,
        forced_tentacles_by_topic,
        activate_strategy_tentacles=activate_strategy_tentacles,
    )
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


def force_tentacles_config_activation(
    tentacles_setup_config, forced_tentacles_by_topic=None, activate_strategy_tentacles=False
):
    _force_tentacles_config_activation(
        tentacles_setup_config,
        forced_tentacles_by_topic,
        activate_strategy_tentacles=activate_strategy_tentacles,
    )


def get_activated_social_services(forced_tentacles_by_topic=None, profile_id=None, requested_sources=None):
    social_services = []
    services_config = get_tentacles_config(forced_tentacles_by_topic, profile_id).tentacles_activation.get(
        octobot_tentacles_manager_constants.TENTACLES_SERVICES_PATH, {}
    )
    requested_sources = {str(source).lower() for source in requested_sources} if requested_sources else set()
    backtestable_feed_by_name = {
        feed_class.get_name(): feed_class
        for feed_class in services_api.get_available_backtestable_feeds()
    }
    for feed_class in class_inspector.get_all_classes_from_parent(services_feeds.AbstractServiceFeed):
        if class_inspector.is_abstract_using_inspection_and_class_naming(feed_class):
            continue
        feed_name = feed_class.get_name()
        if not services_config.get(feed_name, False):
            continue
        backtestable_feed = backtestable_feed_by_name.get(feed_name)
        if backtestable_feed is None:
            continue
        if requested_sources:
            supported_sources = {str(source).lower() for source in (backtestable_feed.get_historical_sources() or [])}
            if not requested_sources.intersection(supported_sources):
                continue
        social_services.append(feed_name)
    return sorted(social_services)


def _get_tentacles_config_path(profile_id=None):
    if profile_id:
        profile = commons_profiles.Profile.load_profile(
            os.path.join(get_module_appdir_path(), commons_constants.USER_PROFILES_FOLDER),
            profile_id,
        )
        return profile.get_tentacles_config_path()
    return os.path.join(
        get_module_appdir_path(),
        octobot_tentacles_manager_constants.USER_REFERENCE_TENTACLE_CONFIG_PATH,
        commons_constants.CONFIG_TENTACLES_FILE
    )


def _get_forced_tentacles_activation(forced_tentacles_by_topic=None, activate_strategy_tentacles=False):
    forced_tentacles = {
        octobot_tentacles_manager_constants.TENTACLES_EVALUATOR_PATH: {},
        octobot_tentacles_manager_constants.TENTACLES_TRADING_PATH: {},
        octobot_tentacles_manager_constants.TENTACLES_SERVICES_PATH: {},
    }
    if activate_strategy_tentacles:
        import tentacles.Evaluator
        forced_tentacles[octobot_tentacles_manager_constants.TENTACLES_EVALUATOR_PATH][
            tentacles.Evaluator.BlankStrategyEvaluator.get_name()
        ] = True
        forced_tentacles[octobot_tentacles_manager_constants.TENTACLES_TRADING_PATH][
            octobot_script.internal.backtester_trading_mode.BacktesterTradingMode.get_name()
        ] = True
    for topic, activations in (forced_tentacles_by_topic or {}).items():
        forced_tentacles.setdefault(topic, {})
        forced_tentacles[topic].update(activations)
    return forced_tentacles


def _force_tentacles_config_activation(
    tentacles_setup_config,
    forced_tentacles_by_topic=None,
    activate_strategy_tentacles=False,
):
    forced_tentacles = _get_forced_tentacles_activation(
        forced_tentacles_by_topic,
        activate_strategy_tentacles=activate_strategy_tentacles,
    )
    for topic, activations in forced_tentacles.items():
        tentacles_setup_config.tentacles_activation.setdefault(topic, {})
        for tentacle, activated in activations.items():
            tentacles_setup_config.tentacles_activation[topic][tentacle] = activated
    if activate_strategy_tentacles:
        _force_backtester_trading_mode(tentacles_setup_config)


def _validate_tentacles_config_source(forced_tentacles_by_topic, profile_id):
    if forced_tentacles_by_topic is not None and profile_id is not None:
        raise ValueError("Only one of tentacles_config or profile_id can be provided.")
    if forced_tentacles_by_topic is not None and not isinstance(forced_tentacles_by_topic, dict):
        raise TypeError("tentacles_config must be a dict keyed by tentacles topic.")


def _force_backtester_trading_mode(tentacles_setup_config):
    trading_path = octobot_tentacles_manager_constants.TENTACLES_TRADING_PATH
    backtester_name = octobot_script.internal.backtester_trading_mode.BacktesterTradingMode.get_name()
    current_trading_modes = tentacles_setup_config.tentacles_activation.get(trading_path, {})
    if current_trading_modes and current_trading_modes != {backtester_name: True}:
        LOGGER.warning(
            'Trading mode is overridden by strategy() function: using BacktesterTradingMode only.'
        )
    tentacles_setup_config.tentacles_activation[trading_path] = {backtester_name: True}
