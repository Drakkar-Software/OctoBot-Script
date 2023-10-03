try:
    from octobot_pro.ai.environments import *
    from octobot_pro.ai.models import *
    from octobot_pro.ai.agents import *

    from gymnasium.envs.registration import register

    register(
        id='TradingEnv',
        entry_point='octobot_pro.ai.environments:TradingEnv',
        disable_env_checker = True
    )
except ImportError:
    pass
