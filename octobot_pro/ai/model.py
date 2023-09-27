from stable_baselines3 import PPO

import os
   
def get_model(environment):
    # Load the model
    if os.path.exists("ppo_trading.zip"):
        model = PPO.load("ppo_trading")

    # instantiate the agent
    model = PPO("MlpPolicy", environment, verbose=1, tensorboard_log="./tensorboard/")

    return model
