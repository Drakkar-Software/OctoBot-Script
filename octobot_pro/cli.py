#  Drakkar-Software OctoBot-Tentacles-Manager
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
import argparse
import asyncio
import aiohttp
import sys

import octobot_commons.logging as commons_logging
import octobot_pro as op
import octobot_pro.internal.octobot_mocks as octobot_mocks
import octobot_pro.internal.logging_util as octobot_pro_logging
import octobot_tentacles_manager.api as api


async def _install_all_tentacles(quite_mode) -> int:
    octobot_pro_logging.enable_base_logger()
    error_count = 0
    logger = commons_logging.get_logger(f"{op.PROJECT_NAME}-CLI")
    install_path = octobot_mocks.get_module_install_path()
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

    if error_count > 0:
        logger.error(f"{error_count} errors occurred while processing tentacles.")
        return 1
    return 0


def handle_octobot_pro_command(starting_args) -> int:
    if starting_args.version:
        print(f"{op.PROJECT_NAME} version {op.VERSION}")
        return 0
    if starting_args.install_tentacles:
        return asyncio.run(_install_all_tentacles(starting_args.quite))
    print(f"No provided command. See --help to get more details on how to use {op.PROJECT_NAME}-CLI", file=sys.stderr)
    return -1


def register_octobot_pro_arguments(parser) -> None:
    parser.add_argument('-v', '--version', help=f'Show {op.PROJECT_NAME} current version.',
                        action='store_true')
    parser.add_argument("-it", "--install-tentacles",
                        help="(Re)-install the available OctoBot tentacles in this modules install directory",
                        action='store_true')
    parser.add_argument("-q", "--quite", help="Only display errors in logs.", action='store_true')


def main():
    parser = argparse.ArgumentParser(prog="octobot_pro", description=f"{op.PROJECT_NAME}-CLI")
    register_octobot_pro_arguments(parser)
    args = parser.parse_args(sys.argv[1:])
    sys.exit(handle_octobot_pro_command(args))


if __name__ == "__main__":
    main()
