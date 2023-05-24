import numpy as np
import pygame
import random
import sys

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

    def seed(self, seed):
        random.seed(seed)
        np.random.seed(seed)

    def render(self):
        self.screen.fill((255, 255, 255))

        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                if cell:
                    text = self.font.render(str(cell), True, (0, 0, 0))
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
        self.generate_board()
        self.clean()

    def step(self, action):
        x, y, n = action

        if self.is_valid(x, y, n):
            self.board[y, x] = n

            if self.board[y].sum() == 45:
                return False, 1
            
            if self.board[:, x].sum() == 45:
                return False, 1
            
            if self.board[y // 3 * 3 : y // 3 * 3 + 3, x // 3 * 3 : x // 3 * 3 + 3].sum() == 45:
                return False, 1

            return False, 0
        
        return True, -100

    def generate_board(self):
        x, y = self.find_empty()

        if x is None:
            return True
        
        nums = np.arange(1, 10)
        np.random.shuffle(nums)

        for i in nums:
            if self.is_valid(x, y, i):
                self.board[x][y] = i

                if self.generate_board():
                    return True
                
                self.board[x][y] = 0

    def find_empty(self):
        # Find the first 0 in self.board
        result = np.where(self.board == 0)
        # print(len(result[0]))
        # print(not  len(result[0]))

        if len(result[0]):
            return result[0][0], result[1][0]
        
        return None, None
    
    def is_valid(self, x, y, n):
        # Check if row fits
        if n in self.board[x]:
            return False
        
        # Check if column fits
        if n in self.board[:, y]:
            return False
        
        # Check if square fits
        x0 = (x // 3) * 3
        y0 = (y // 3) * 3
        for i in range(3):
            for j in range(3):
                if self.board[x0 + i][y0 + j] == n:
                    return False
                
        return True
    
    def clean(self):
        for i in range(9):
            delete_indices = np.arange(9)
            np.random.shuffle(delete_indices)
            print(delete_indices)

            for delete in delete_indices[random.randrange(9):]:
                self.board[i, delete] = 0

    

if __name__ == "__main__":
    game = SudokuGame()
    game.reset()
    print(game.board)

    while True:
        game.render()
        