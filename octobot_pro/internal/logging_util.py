import logging
import logging.config as config
import os.path

import octobot.logger
import octobot.constants


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
        config.fileConfig(octobot.constants.LOGGING_CONFIG_FILE)
    octobot.logger.init_bot_channel_logger()


def enable_base_logger():
    logging.basicConfig(
        level=logging.DEBUG,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="%(asctime)s %(levelname)-8s %(name)-20s %(message)s"
    )

