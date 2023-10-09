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


import click
import asyncio
import aiohttp
import sys

import octobot_script
import octobot_script.internal.octobot_mocks as octobot_mocks
import octobot_script.internal.logging_util as octobot_script_logging
import octobot_tentacles_manager.api as api


async def install_all_tentacles(quite_mode) -> bool:
    octobot_script_logging.enable_base_logger()
    error_count = 0
    install_path = octobot_mocks.get_module_appdir_path()
    tentacles_path = octobot_mocks.get_tentacles_path()
    tentacles_urls = octobot_mocks.get_public_tentacles_urls()
    async with aiohttp.ClientSession() as aiohttp_session:
        for tentacles_url in tentacles_urls:
            error_count += await api.install_all_tentacles(tentacles_url,
                                                           tentacle_path=tentacles_path,
                                                           bot_path=install_path,
                                                           aiohttp_session=aiohttp_session,
                                                           quite_mode=quite_mode,
                                                           bot_install_dir=install_path)
    return error_count == 0


@click.group
@click.version_option(version=octobot_script.VERSION, prog_name=octobot_script.PROJECT_NAME)
def main():
    """
    OctoBot-Script command line interface.
    """


@main.command("install_tentacles")
@click.option('--quite', flag_value=True, help='Only display errors in logs.')
def sync_install_tentacles(quite):
    """
    (Re)-install the available OctoBot tentacles.
    """
    sys.exit(0 if asyncio.run(install_all_tentacles(quite)) else -1)


if __name__ == "__main__":
    main()
