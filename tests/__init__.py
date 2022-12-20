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
