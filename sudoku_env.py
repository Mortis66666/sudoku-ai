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
        # self.observation_space = gym.spaces.Box(
        #     low=np.array([1, 1, -1]),
        #     high=np.array([9, 9, 1]),
        #     dtype=int
        # )
        self.observation_space = gym.spaces.Box(
            low=-1,
            high=9,
            shape=(9, 9, 2),
            dtype=int
        )

        # print("obs space:")
        # print(self.observation_space)

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
        return self.generate_observation(), reward, self.done, {}

    def render(self, mode="human", close=False):
        now = time.time()

        if now - self.last_render < self.frame_delay:
            return
        
        self.last_render = now

        self.game.render()

    def reset(self):
        self.steps = 0
        self.reward = 0
        self.game.reset()
        return self.generate_observation()

    def get_action_mask(self):
        # print(self.game.board)
        action_mask = np.zeros(self.action_space.n, dtype=bool)

        for action_index in range(self.action_space.n):
            x, y, _ = self.get_action_details(action_index)
            if self.game.board[y, x] == 0 or (x, y) in self.game.player_place:
                action_mask[action_index] = True

        return action_mask
    
    def get_action_details(self, action_index):
        x = action_index // (9 * 9)
        y = (action_index // 9) % 9
        value = action_index % 9
        return x, y, value
    
    def generate_observation(self):
        obs = np.zeros((9, 9, 2))

        for y, cell in enumerate(self.game.board):
            for x, value in enumerate(cell):

                if (x, y) in self.game.player_place:
                    self.game.board[y, x] = 0

                    if self.game.is_valid(x, y, value):
                        obs[y, x, 1] = 1
                    else:
                        obs[y, x, 1] = -1

                    self.game.board[y, x] = value


                obs[y, x, 0] = value

        return obs

if __name__ == "__main__":
    env = SudokuEnv()
    env.reset()

    print(env.step((0, 0, 5)))