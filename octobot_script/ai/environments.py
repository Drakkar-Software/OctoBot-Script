# pylint: disable=maybe-no-member
import gymnasium as gym
from gymnasium import spaces
import numpy as np

import octobot_script as obs
import octobot_trading.errors as octobot_trading_errors
import octobot_trading.api as trading_api

def basic_reward_function(current_portfolio_value, previous_portfolio_value, current_profitability, market_profitability, created_orders):
    if previous_portfolio_value is None:
        return 0
    try:
        pf_reward = np.log(float(current_portfolio_value) / float(previous_portfolio_value))
        prof_reward = np.log(float(current_profitability) / float(market_profitability))
        reward = 0 if np.isnan(pf_reward) else pf_reward + 0 if np.isnan(prof_reward) else prof_reward
        return reward
    except ZeroDivisionError:
        return 0

async def basic_trade_function(ctx, actions):
    try:
        (
            order_type,
            order_amount,
            order_price_offset,
            stop_loss_or_take_profit,
        ) = list(actions)
        real_order_amout = min(abs(order_amount), 1) * 30 # max 30%
        real_order_price_offset = min(abs(order_price_offset), 1) * 10

        real_take_profit_offset = 0
        real_stop_loss_offset = 0
        if stop_loss_or_take_profit > 0:
            real_take_profit_offset = min(abs(stop_loss_or_take_profit), 1) * 10
        elif stop_loss_or_take_profit < 0:
            real_stop_loss_offset = min(abs(stop_loss_or_take_profit), 1) * 10

        created_orders = []
        if order_type > 0.66:
            created_orders.append(await obs.market(
                ctx,
                "buy",
                amount=f"{real_order_amout}%",
                stop_loss_offset=f"-{real_stop_loss_offset}%" if real_stop_loss_offset != 0 else None,
                take_profit_offset=f"{real_take_profit_offset}%" if real_take_profit_offset != 0 else None,
            ))
        elif order_type > 0.33:
            created_orders.append(await obs.market(
                ctx,
                "sell",
                amount=f"{real_order_amout}%",
                stop_loss_offset=f"{real_stop_loss_offset}%" if real_stop_loss_offset != 0 else None,
                take_profit_offset=f"-{real_take_profit_offset}%" if real_take_profit_offset != 0 else None,
            ))
        if order_type > 0:
            created_orders.append(await obs.limit(
                ctx,
                "buy",
                amount=f"{real_order_amout}%",
                offset=f"-{real_order_price_offset}%",
                stop_loss_offset=f"-{real_stop_loss_offset}%" if real_stop_loss_offset != 0 else None,
                take_profit_offset=f"{real_take_profit_offset}%" if real_take_profit_offset != 0 else None,
            ))
        if order_type > -0.33:
            created_orders.append(await obs.limit(
                ctx,
                "sell",
                amount=f"{real_order_amout}%",
                offset=f"{real_order_price_offset}%",
                stop_loss_offset=f"{real_stop_loss_offset}%" if real_stop_loss_offset != 0 else None,
                take_profit_offset=f"-{real_take_profit_offset}%" if real_take_profit_offset != 0 else None,
            ))
        else:
            # Nothing for now
            # cancel orders, idle ?
            pass
        return created_orders
    except TypeError:
        pass

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
                action_types=[0],
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

        self.traded_symbols = traded_symbols
        self.static_features = [] # TODO there are computed once before being used in the environement
        self.dynamic_feature_functions = dynamic_feature_functions #  are computed at each step of the environment
        self._nb_features = 59 + len(self.traded_symbols) * 4 + len(self.static_features) + len(self.dynamic_feature_functions)

        self.reward_function = reward_function
        self.trade_function = trade_function
        self.max_episode_duration = max_episode_duration
        
        self.action_space = spaces.Box(low=-1, high=1, shape=(len(action_types),))  # 3 float in range [0, 1]
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
            created_orders = await self.trade_function(ctx, content)
        except octobot_trading_errors.PortfolioNegativeValueError:
            forced_reward = -1

        self._idx += 1
        self._step += 1

        done, truncated = False, False

        if not done and forced_reward is None:
            current_pf_value = get_current_portfolio_value(ctx)
            profitabilities = get_profitabilities(ctx)
            current_profitability = profitabilities[1]
            market_profitability = profitabilities[3]
            reward = self.reward_function(current_pf_value, 
                                          self._previous_portfolio_value, 
                                          current_profitability, 
                                          market_profitability,
                                          created_orders)
            self._previous_portfolio_value = current_pf_value
        else:
            reward = forced_reward
        # TODO save reward

        if done or truncated:
            # TODO ?
            None
        return await self.get_obs(ctx), reward, done, truncated
