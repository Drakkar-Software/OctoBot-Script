import asyncio
import tulipy
import gymnasium as gym
from tqdm import tqdm
import numpy as np

import argparse
import octobot_commons.symbols as symbols
import octobot_pro as op

async def basic_evaluation_function(ctx):
    closes = await op.Close(ctx, max_history=True)
    open = await op.Open(ctx, limit=30)
    high = await op.High(ctx, limit=30)
    low = await op.Low(ctx, limit=30)
    vol = await op.Volume(ctx, limit=30)
    #rsi_v = tulipy.rsi(closes, period=10)
    return np.array([
        open[-1] if len(open) > 0 else 0,
        high[-1] if len(high) > 0 else 0,
        low[-1]  if len(low) > 0 else 0,
        closes[-1]  if len(closes) > 0 else 0,
        vol[-1]  if len(vol) > 0 else 0,
        #   rsi_v[-1],
    ], dtype=np.float32)

async def run_strategy(data, env, model, symbol, time_frame, is_training=False, plot=False): 
    async def strategy(ctx):
        if not env.env.get_wrapper_attr('is_reset'):
            observation = await env.reset(options={
                'ctx': ctx
            })

        action = env.action_space.sample() if is_training else model.predict(await env.get_obs(ctx))[0]
        observation, reward, done, truncated = await env.step({
            'ctx': ctx,
            'content': action
        })

    # Run a backtest using the above data, strategy and configuration.
    res = await op.run(data, strategy, {}, enable_logs=False)

    if plot:
        print(res.describe())
        await res.plot(show=True)

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--count", default="1")
    parser.add_argument("-t", "--train", action=argparse.BooleanOptionalAction)
    parser.add_argument("-tt", "--train-timesteps", default="10000")
    parser.add_argument("-p", "--plot", action=argparse.BooleanOptionalAction)
    return parser


def main():
    parser = init_argparse()
    args = parser.parse_args()

    symbol = symbols.parse_symbol("BTC/USDT")
    time_frame = "1d"
    data = asyncio.run(op.get_data(symbol.merged_str_symbol(), time_frame, start_timestamp=1505606400))

    gym_env = gym.make(id='TradingEnv', name= "test", dynamic_feature_functions=[basic_evaluation_function], traded_symbols=[symbol])
    model = op.get_model(gym_env)

    # Train the model
    # if args.train:
    #     for i in tqdm(range(int(args.count))):
    #         asyncio.run(run_strategy(data, gym_env, model, symbol, time_frame, is_training=args.train, plot=args.plot))
        # model.learn(total_timesteps=int(args.train_timesteps), callback=op.TensorboardCallback())
    
    # Test
    for i in tqdm(range(int(args.count))):
        asyncio.run(run_strategy(data, gym_env, model, symbol, time_frame, is_training=args.train, plot=args.plot))

    asyncio.run(data.stop())

    # Save the model
    model.save("ppo_trading")


main()
