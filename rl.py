import asyncio
import tulipy
import gymnasium as gym
from tqdm import tqdm
import numpy as np
import time
import re

import argparse
import octobot_commons.symbols as symbols
import octobot_pro as op

async def basic_evaluation_function(ctx):
    closes = await op.Close(ctx, max_history=True)
    open = await op.Open(ctx, limit=30)
    high = await op.High(ctx, limit=30)
    low = await op.Low(ctx, limit=30)
    vol = await op.Volume(ctx, limit=30)
    rsi_v = tulipy.rsi(closes, period=10)

    if (len(rsi_v) > 5 and len(closes) > 5):
        return np.array([
            closes[-5:],
            vol[-5:],
            rsi_v[-5:],
        ], dtype=np.float32).flatten()
    else:
        return np.zeros(15, dtype=np.float32) 

async def run_strategy(data, env, agent, symbol, time_frame, is_training=False, plot=False):
    async def strategy(ctx):
        state = None
        if not env.env.get_wrapper_attr('is_reset'):
            state = await env.reset(options={
                'ctx': ctx
            })
        else:
            state = await env.get_obs(ctx)
            
        action = agent.act(state)
        next_state, reward, done, info = await env.step({
            'ctx': ctx,
            'content': action
        })

        if is_training:
            agent.remember(state, action, reward, next_state, done)  

    # Run a backtest using the above data, strategy and configuration.
    res = await op.run(data, strategy, {}, enable_logs=False)

    if plot:
        print(res.describe())
        await res.plot(show=True)

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--episode", type=int, default=1)
    parser.add_argument('-b', '--batch_size', type=int, default=32,
                        help='batch size for experience replay')
    parser.add_argument("-t", "--train", action=argparse.BooleanOptionalAction)
    parser.add_argument("-p", "--plot", action=argparse.BooleanOptionalAction)
    parser.add_argument('-w', '--weights', type=str, help='a trained model weights')
    return parser


def main():
    parser = init_argparse()
    args = parser.parse_args()

    timestamp = time.strftime('%Y%m%d%H%M')
    symbol = symbols.parse_symbol("BTC/USDT")
    time_frame = "1d"
    data = asyncio.run(op.get_data(symbol.merged_str_symbol(), time_frame, exchange='binance', start_timestamp=1505606400))

    gym_env = gym.make(id='TradingEnv', name= "test", dynamic_feature_functions=[basic_evaluation_function], traded_symbols=[symbol])
    agent = op.DQNAgent(4)

    if not args.train:
        # load trained weights
        agent.load(args.weights)
        
        # when test, the timestamp is same as time when weights was trained
        timestamp = re.findall(r'\d{12}', args.weights)[0]

    for episode in range(args.episode):
        print(f"Starting episode {episode}...") 
        asyncio.run(run_strategy(data, gym_env, agent, symbol, time_frame, is_training=args.train, plot=args.plot))
        
        if args.train and len(agent.memory) > args.batch_size:
            print("Starting replay...")
            agent.replay(args.batch_size)

        if args.train and (episode + 1) % 10 == 0:  # checkpoint weights
            print("Saving...")
            agent.save(f"weights/{timestamp}-dqn.h5")

    if args.train:
        agent.save(f"weights/{timestamp}-final-dqn.h5")

    asyncio.run(data.stop())

main()
