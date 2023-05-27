import json
import math
import numpy as np
import pygame
import random
import sys
import time

# from joblib import transient

MAX_STEPS = 1000

class SudokuGame:
    def __init__(self, seed=None, log_data=False):
        if seed:
            self.seed(seed)

        self.log_data = log_data

        pygame.init()
        pygame.font.init()

        self.size = 666
        self.cell_size = self.size / 9

        self.screen = pygame.display.set_mode((self.size, self.size))
        pygame.display.set_caption("Sudoku Game")

        self.font = pygame.font.SysFont("Arial", 30)

        self.player_place = set()
        self.steps = 0

        self.selected_x = 0
        self.selected_y = 0

        self.row_progress = 0
        self.col_progress = 0
        self.box_progress = 0
        self.avg_progress = 0


        self.data = {
            "row_progress": [],
            "col_progress": [],
            "box_progress": [],
            "avg_progress": []
        }

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
                if x == self.selected_x and y == self.selected_y:
                    pygame.draw.rect(
                        self.screen,
                        (220, 220, 220),
                        (
                            self.selected_x * self.cell_size,
                            self.selected_y * self.cell_size,
                            self.cell_size,
                            self.cell_size
                        )
                    )

                if self.board[y, x] == 0 or (x, y) in self.player_place:
                    pygame.draw.rect(
                        self.screen,
                        (255, 255, 204),
                        (
                            x * self.cell_size,
                            y * self.cell_size,
                            self.cell_size,
                            self.cell_size
                        )
                    )

                if cell:
                    color = (0, 0, 0)

                    self.board[y, x] = 0

                    if (x, y) in self.player_place:
                        if self.is_valid(x, y, cell):
                            color = (0, 255, 0)
                        else:
                            color = (255, 0, 0)

                    self.board[y, x] = cell

                    text = self.font.render(str(cell), True, color)
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_UP:
                    self.selected_y = max(0, self.selected_y - 1)
                elif event.key == pygame.K_DOWN:
                    self.selected_y = min(8, self.selected_y + 1)
                elif event.key == pygame.K_LEFT:
                    self.selected_x = max(0, self.selected_x - 1)
                elif event.key == pygame.K_RIGHT:
                    self.selected_x = min(8, self.selected_x + 1)
                elif event.key >= pygame.K_1 and event.key <= pygame.K_9:
                    n = event.key - pygame.K_1 + 1
                    self.put(self.selected_x, self.selected_y, n)
                elif event.key in (pygame.K_BACKSPACE, pygame.K_0):
                    self.board[self.selected_y, self.selected_x] = 0
                    self.player_place.remove((self.selected_x, self.selected_y))

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()

                self.selected_x = math.floor(x / self.cell_size)
                self.selected_y = math.floor(y / self.cell_size)

    def reset(self):
        self.board = np.zeros((9, 9), dtype=int)
        # self.board[0] = np.arange(1, 10)
        # np.random.shuffle(self.board[0])
        self.generate_board()
        self.clean()
        self.player_place.clear()
        self.log_data = self.data = {
            "row_progress": [],
            "col_progress": [],
            "box_progress": [],
            "avg_progress": []
        }
        self.steps = 0

    def step(self, action):
        x, y, n = action
        self.steps += 1

        done = False
        reward = 0

        # Finish game if reach max steps
        if self.steps > MAX_STEPS:
            done = True

        # Encourage ai to explore
        if self.board[y, x] == 0:
            reward += 1
        else:
            reward -= 1

        self.put(x, y, n)

        _x, _ = self.find_empty()

        if _x is None:
            reward += 3
            done = True

        self.row_progress = self.calculate_progress(self.board[y])
        self.col_progress = self.calculate_progress(self.board[:, x])
        self.box_progress = self.calculate_progress(self.board[y // 3 * 3 : y // 3 * 3 + 3, x // 3 * 3 : x // 3 * 3 + 3])
        self.avg_progress = (self.row_progress + self.col_progress + self.box_progress) / 3


        self.board[y, x] = 0

        if self.is_valid(x, y, n):
            reward += self.avg_progress * 5
        else:
            reward -= (1 - self.avg_progress) * 5

        self.board[y, x] = n
        
        if self.log_data:
            self.data["row_progress"].append(self.row_progress)
            self.data["col_progress"].append(self.col_progress)
            self.data["box_progress"].append(self.box_progress)
            self.data["avg_progress"].append(self.avg_progress)

            with open("data.json", "w") as f:
                json.dump(self.data, f, indent=4)

        return done, reward, self.steps

    def put(self, x, y, n):
        self.board[y, x] = n
        self.player_place.add((x, y))

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

    def check_unique(self, arr):
        return np.all(np.isin(np.arange(1, 10), arr))

    def calculate_progress(self, arr: np.ndarray):
        target = np.arange(1, 10)  # Array with numbers 1 to 9
        intersection = np.intersect1d(arr.flatten(), target)
        similarity = len(intersection) / len(target)
        return similarity
    
    def is_valid(self, x, y, n):
        # if self.board[y, x] != 0 and (x, y) not in self.player_place:
        #     return False

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
        