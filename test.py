import json
import time
import random

from sb3_contrib import MaskablePPO
from sudoku_env import SudokuEnv


with open("config.json", "r") as f:
    config = json.load(f)


MODEL_PATH = config["model_path"]
NUM_EPISODE = config["num_episode"]
RENDER = config["render"]
FRAME_DELAY = config["frame_delay"] # 0.01 fast, 0.05 slow
ROUND_DELAY = config["round_delay"]

seed = random.randint(0, 1e9)
print(f"Using seed = {seed} for testing.")

env = SudokuEnv(seed=seed)


# Load the trained model
model = MaskablePPO.load(MODEL_PATH)

total_reward = 0
total_score = 0
min_score = 1e9
max_score = 0

for episode in range(NUM_EPISODE):
    obs = env.reset()
    episode_reward = 0
    done = False
    
    info = None

    sum_step_reward = 0

    retry_limit = 9
    print(f"=================== Episode {episode + 1} ==================")
    while not done:
        action, _ = model.predict(obs, action_masks=env.get_action_mask())
        prev_mask = env.get_action_mask()
        obs, reward, done, info = env.step(action)

        # if done:
        #     if info["snake_size"] == env.game.grid_size:
        #         print(f"You are BREATHTAKING! Victory reward: {reward:.4f}.")
        #     else:
        #         last_action = ["UP", "LEFT", "RIGHT", "DOWN"][action]
        #         print(f"Gameover Penalty: {reward:.4f}. Last action: {last_action}")

        # elif info["food_obtained"]:
        #     print(f"Food obtained at step {num_step:04d}. Food Reward: {reward:.4f}. Step Reward: {sum_step_reward:.4f}")
        #     sum_step_reward = 0 

        # else:
        sum_step_reward += reward
        episode_reward += reward

        if RENDER:
            env.render()
            time.sleep(FRAME_DELAY)


    
    print(f"Episode {episode + 1}: Reward Sum: {episode_reward:.4f}")
    total_reward += episode_reward
    total_score += env.game.score
    if RENDER:
        time.sleep(ROUND_DELAY)

env.close()
print(f"=================== Summary ==================")
print(f"Average Score: {total_score / NUM_EPISODE}, Min Score: {min_score}, Max Score: {max_score}, Average reward: {total_reward / NUM_EPISODE}")