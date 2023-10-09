try:
    from octobot_script.ai.environments import *
    from octobot_script.ai.models import *
    from octobot_script.ai.agents import *

    from gymnasium.envs.registration import register

    register(
        id='TradingEnv',
        entry_point='octobot_script.ai.environments:TradingEnv',
        disable_env_checker = True
    )
except ImportError:
    pass
