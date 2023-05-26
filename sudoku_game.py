import numpy as np
import pygame
import random
import sys
import time

# from joblib import transient

MAX_STEPS = 1000

class SudokuGame:
    def __init__(self, seed=None):
        if seed:
            self.seed(seed)

        pygame.init()
        pygame.font.init()

        self.size = 666
        self.cell_size = self.size / 9

        self.screen = pygame.display.set_mode((self.size, self.size))
        pygame.display.set_caption("Sudoku Game")

        self.font = pygame.font.SysFont("Arial", 30)

        self.reds = []
        self.steps = 0

        # self.screen = transient(self.screen)
        # self.font = transient(self.font)

    def seed(self, seed):
        random.seed(seed)
        np.random.seed(seed)

    def render(self):
        # print('render')

        self.screen.fill((255, 255, 255))

        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                if cell:
                    text = self.font.render(str(cell), True, (255, 0, 0) if (x, y) in self.reds else (0, 0, 0))
                    self.screen.blit(
                        text,
                        (
                            x * self.cell_size + (self.cell_size - text.get_width()) / 2,
                            y * self.cell_size + (self.cell_size - text.get_height()) / 2,
                        )
                    )

        # Draw line
        for i in range(1, 9):
            extra = (not bool(i % 3)) * 2
            pygame.draw.line(
                self.screen,
                (0, 0, 0),
                (0, i * self.cell_size),
                (self.size, i * self.cell_size),
                2 + extra
            )

            pygame.draw.line(
                self.screen,
                (0, 0, 0),
                (i * self.cell_size, 0),
                (i * self.cell_size, self.size),
                2 + extra
            )

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def reset(self):
        self.board = np.zeros((9, 9), dtype=int)
        # self.board[0] = np.arange(1, 10)
        # np.random.shuffle(self.board[0])
        self.generate_board()
        self.clean()
        self.reds.clear()
        self.steps = 0

        return self.board

    def step(self, action):
        x, y, n = action
        self.steps += 1

        done = False
        reward = 0

        if self.steps > MAX_STEPS:
            done = True

        elif self.is_valid(x, y, n):
            reward += .1

            self.put(x, y, n)

            x, _ = self.find_empty()

            if x is None:
                reward += 3
                done = True

            if self.board[y].sum() == 45:
                reward += 1
            
            elif self.board[:, x].sum() == 45:
                reward += 1
            
            elif self.board[y // 3 * 3 : y // 3 * 3 + 3, x // 3 * 3 : x // 3 * 3 + 3].sum() == 45:
                reward += 1
        
        else:
            reward -= .5
        
        return done, reward, self.steps

    def put(self, x, y, n):
        self.board[y, x] = n
        self.reds.append((x, y))

    def generate_board(self):
        base  = 3
        side  = base*base

        # pattern for a baseline valid solution
        def pattern(r,c):
            return (base*(r%base)+r//base+c)%side

        # randomize rows, columns and numbers (of valid base pattern)
        def shuffle(s):
            return random.sample(s,len(s)) 
        
        rBase = range(base)
        rows  = [ g*base + r for g in shuffle(rBase) for r in shuffle(rBase) ] 
        cols  = [ g*base + c for g in shuffle(rBase) for c in shuffle(rBase) ]
        nums  = shuffle(range(1,base*base+1))

        # produce board using randomized baseline pattern
        self.board = np.array([ [nums[pattern(r,c)] for c in cols] for r in rows ], dtype=int)

    def find_empty(self):
        # Find the first 0 in self.board
        result = np.where(self.board == 0)
        # print(len(result[0]))
        # print(not  len(result[0]))

        if len(result[0]):
            return result[0][0], result[1][0]
        
        return None, None
    
    def is_valid(self, x, y, n):
        if self.board[y, x] != 0 and (x, y) not in self.reds or self.board[y, x] == n:
            return False

        # Check if row fits
        if n in self.board[y]:
            return False
        
        # Check if column fits
        if n in self.board[:, x]:
            return False
        
        # Check if the number already exists in the 3x3 grid
        start_row = (y // 3) * 3
        start_col = (x // 3) * 3
        if n in self.board[start_row:start_row + 3, start_col:start_col + 3]:
            return False
                
        return True
    
    def clean(self):
        for i in range(9):
            delete_indices = np.arange(9)
            np.random.shuffle(delete_indices)
            # print(delete_indices)

            for delete in delete_indices[random.randrange(9):]:
                self.board[i, delete] = 0

    

if __name__ == "__main__":
    game = SudokuGame()
    game.reset()
    print(game.board)

    while True:
        game.render()
        