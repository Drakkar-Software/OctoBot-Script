import os
import json
import octobot_tentacles_manager.api as octobot_tentacles_manager_api


def get_tentacles_config():
    return octobot_tentacles_manager_api.get_tentacles_setup_config(_mock_file_path("tentacles_config.json"))


def get_config():
    with open(_mock_file_path("config_mock.json")) as f:
        return json.load(f)


def _mock_file_path(file_name):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)
