#  This file is part of OctoBot-Pro (https://github.com/Drakkar-Software/OctoBot-Pro)
#  Copyright (c) 2022 Drakkar-Software, All rights reserved.
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
#  License along with OctoBot-Pro. If not, see <https://www.gnu.org/licenses/>.

import pytest
import mock
import octobot_pro.internal.octobot_mocks as octobot_mocks


# only load config once
TEST_CONFIG = octobot_mocks.get_config()
TEST_TENTACLES_CONFIG = octobot_mocks.get_tentacles_config()


@pytest.fixture
def mocked_config():
    with mock.patch.object(octobot_mocks, "get_config", mock.Mock(return_value=TEST_CONFIG)), \
          mock.patch.object(octobot_mocks, "get_tentacles_config", mock.Mock(return_value=TEST_TENTACLES_CONFIG)):
        yield
