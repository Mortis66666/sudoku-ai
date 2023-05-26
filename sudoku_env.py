import gym
import numpy as np
import time
from sudoku_game import SudokuGame

class SudokuEnv(gym.Env):
    def __init__(self, seed=0):
        super().__init__()

        self.game = SudokuGame(seed)
        self.game.reset()

        self.action_space = gym.spaces.discrete.Discrete(9 * 9 * 9)
        self.observation_space = gym.spaces.Box(low=0, high=9, shape=(9, 9), dtype=int)

        self.done = False
        self.steps = 0
        self.reward = 0

        self.last_render = 0
        self.frame_delay = 0.05


    def seed(self, seed=0):
        self.game.seed(seed)

    def step(self, action):
        self.done, reward, self.steps = self.game.step(self.get_action_details(action))
        self.reward += reward
        return self.game.board, reward, self.done, {}

    def render(self):
        now = time.time()

        if now - self.last_render < self.frame_delay:
            return
        
        self.last_render = now

        self.game.render()

    def reset(self):
        self.steps = 0
        self.reward = 0
        return self.game.reset()

    def get_action_mask(self):
        action_mask = np.zeros(self.action_space.n, dtype=bool)

        for action_index in range(self.action_space.n):
            row, col, value = self.get_action_details(action_index)
            action = (row, col, value)
            if self.game.is_valid(*action):
                action_mask[action_index] = True

        return action_mask
    
    def get_action_details(self, action_index):
        row = action_index // (9 * 9)
        col = (action_index // 9) % 9
        value = action_index % 9
        return row, col, value

if __name__ == "__main__":
    env = SudokuEnv()
    env.reset()

    print(env.step((0, 0, 5)))