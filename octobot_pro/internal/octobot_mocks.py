import os
import json

import octobot_pro.constants as constants
import octobot_tentacles_manager.api as octobot_tentacles_manager_api
import octobot_tentacles_manager.constants as octobot_tentacles_manager_constants
import octobot.configuration_manager as octobot_configuration_manager


def get_tentacles_config():
    return octobot_tentacles_manager_api.get_tentacles_setup_config(
        get_module_config_path("tentacles_config.json")
    )


def get_config():
    with open(get_module_config_path("config_mock.json")) as f:
        return json.load(f)


def get_module_install_path():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_module_config_path(file_name):
    return os.path.join(get_module_install_path(), constants.CONFIG_PATH, file_name)


def get_internal_import_path():
    return os.path.join(get_module_install_path(), constants.ADDITIONAL_IMPORT_PATH)


def get_imported_tentacles_path():
    import tentacles
    return os.path.dirname(os.path.abspath(tentacles.__file__))


def get_tentacles_path():
    return os.path.join(get_internal_import_path(), octobot_tentacles_manager_constants.TENTACLES_PATH)


def get_public_tentacles_urls():
    return [
        octobot_configuration_manager.get_default_tentacles_url()
    ]
