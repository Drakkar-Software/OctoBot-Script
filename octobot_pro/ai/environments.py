import gymnasium as gym
from gymnasium import spaces
import numpy as np

import octobot_pro as op
import octobot_trading.errors as octobot_trading_errors
import octobot_trading.api as trading_api

def basic_reward_function(current_portfolio_value, previous_portfolio_value):
    if previous_portfolio_value is None:
        return 0
    return np.log(float(current_portfolio_value) / float(previous_portfolio_value))

async def basic_trade_function(ctx, action):
    (
        action_type,
        amount,
        price_offset,
        stop_loss_offset,
        take_profit_offset,
    ) = list(action)

    if action_type > 50:
        await op.market(
            ctx,
            "buy",
            amount=f"{abs(amount)}%",
            stop_loss_offset=f"{stop_loss_offset}%",
            take_profit_offset=f"{take_profit_offset}%",
        )
    elif action_type > 0:
        await op.market(
            ctx,
            "sell",
            amount=f"{abs(amount)}%",
            stop_loss_offset=f"{stop_loss_offset}%",
            take_profit_offset=f"{take_profit_offset}%",
        )
    elif action_type > -50:
        await op.limit(
            ctx,
            "buy",
            amount=f"{abs(amount)}%",
            offset=f"{price_offset}%",
            stop_loss_offset=f"{stop_loss_offset}%",
            take_profit_offset=f"{take_profit_offset}%",
        )
    else:
        await op.limit(
            ctx,
            "sell",
            amount=f"{abs(amount)}%",
            offset=f"{price_offset}%",
            stop_loss_offset=f"{stop_loss_offset}%",
            take_profit_offset=f"{take_profit_offset}%",
        )

# TODO move somewhere else
def get_profitabilities(ctx):
    return trading_api.get_profitability_stats(ctx.exchange_manager)

# TODO move somewhere else
def get_open_orders(ctx):
    return [] # TODO

# TODO move somewhere else
def get_current_portfolio_value(ctx):
    return trading_api.get_current_portfolio_value(ctx.exchange_manager)

# TODO move somewhere else
def get_current_portfolio(ctx):
    return trading_api.portfolio.get_portfolio(ctx.exchange_manager)

def get_flatten_pf(current_portfolio, symbol):
    return np.array([float(current_portfolio[symbol.base].available), 
                    float(current_portfolio[symbol.base].total), 
                    float(current_portfolio[symbol.quote].available), 
                    float(current_portfolio[symbol.quote].total)], dtype=np.float32)

class TradingEnv(gym.Env):
    def __init__(self,
                action_types : list = [0, 0, 0, 0, 0],
                dynamic_feature_functions = [],
                reward_function = basic_reward_function,
                trade_function = basic_trade_function,
                max_episode_duration = 'max',
                verbose = 1,
                name = "Rl",
                traded_symbols=[]
                ):
        self.max_episode_duration = max_episode_duration
        self.name = name
        self.verbose = verbose
        self.is_reset = False

        self.action_types = action_types
        self.traded_symbols = traded_symbols
        self.static_features = [] # TODO there are computed once before being used in the environement
        self.dynamic_feature_functions = dynamic_feature_functions #  are computed at each step of the environment
        self._nb_features = 4 + len(self.traded_symbols) * 4 + len(self.static_features) + len(self.dynamic_feature_functions)

        self.reward_function = reward_function
        self.trade_function = trade_function
        self.max_episode_duration = max_episode_duration
        
        self.action_space = spaces.Box(low=-100, high=100, shape=(5,))  # 5 float in range [-100, 100]
        self.observation_space = spaces.Box(
            -np.inf,
            np.inf,
            shape = [self._nb_features]
        )

        self.log_metrics = []
        self._previous_portfolio_value = None
    
    async def get_obs(self, ctx):
        flatten_pf = np.concatenate([get_flatten_pf(get_current_portfolio(ctx), symbol) for symbol in self.traded_symbols])
        # TODO open orders
        dynamic_obs = []
        for dynamic_feature_function in self.dynamic_feature_functions:
            dynamic_obs.append(await dynamic_feature_function(ctx))
        return np.concatenate([dynamic_obs[0], flatten_pf])

    async def reset(self, seed = None, options = None):
        super().reset(seed = seed)
        self.is_reset = True
        self._step = 0
        self._idx = 0
        if self.max_episode_duration != 'max':
            self._idx = np.random.randint(
                low = self._idx, 
                high = len(self.df) - self.max_episode_duration - self._idx
            )

        return await self.get_obs(options['ctx'])
            
    async def step(self, action):
        ctx = action['ctx']
        content = action['content']
    
        forced_reward = None
        # take content
        try: 
            await self.trade_function(ctx, content)
        except octobot_trading_errors.PortfolioNegativeValueError:
            forced_reward = -1

        self._idx += 1
        self._step += 1

        done, truncated = False, False

        if not done and forced_reward is None:
            current_pf_value = get_current_portfolio_value(ctx)
            reward = self.reward_function(current_pf_value, self._previous_portfolio_value)
            self._previous_portfolio_value = current_pf_value
        else:
            reward = forced_reward
        # TODO save reward

        if done or truncated:
            # TODO ?
            None
        return await self.get_obs(ctx), reward, done, truncated
