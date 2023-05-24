import gymnasium as gym
import numpy as np
from sudoku_game import SudokuGame

class SudokuEnv(gym.Env):
    def __init__(self, seed=0):
        super().__init__()

        self.game = SudokuGame(seed)
        self.game.reset()

        self.action_space = gym.spaces.Tuple((
            gym.spaces.Discrete(9),  # Row index (0-8)
            gym.spaces.Discrete(9),  # Column index (0-8)
            gym.spaces.Discrete(9)   # Cell value (1-9)
        ))
        self.observation_space = gym.spaces.Box(low=0, high=9, shape=(9, 9), dtype=int)

        self.done = False

    def seed(self, seed=0):
        self.game.seed(seed)

    def step(self, action):
        self.done, reward = self.step(action)

        return self.game.board, reward, self.done, {}

    def render(self):
        self.game.render()

    def reset(self):
        self.game.reset()

    def get_action_mask(self):
        action_mask = np.zeros(self.action_space.n, dtype=bool)
    
        for row in range(9):
            for col in range(9):
                for value in range(1, 10):
                    action = (row, col, value)
                    if self.game.is_valid(*action):
                        action_index = self.action_space.index(action)
                        action_mask[action_index] = True
        
        return action_mask