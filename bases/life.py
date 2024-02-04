import pygame
import numpy as np
import time

pygame.init()

# Configurações
width, height = 600, 600
cell_size = 10
rows, cols = height // cell_size, width // cell_size
game_board = np.random.choice([0, 1], size=(rows, cols), p=[0.9, 0.1])

# Cores
bg_color = (255, 255, 255)
cell_color = (0, 0, 0)

# Inicialização da janela
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Conway's Game of Life")

def update_board(board):
    new_board = np.copy(board)
    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            neighbors = board[i - 1 : i + 2, j - 1 : j + 2].sum() - board[i, j]
            if board[i, j] == 1 and (neighbors < 2 or neighbors > 3):
                new_board[i, j] = 0
            elif board[i, j] == 0 and neighbors == 3:
                new_board[i, j] = 1
    return new_board

def draw_board(board):
    screen.fill(bg_color)
    for i in range(rows):
        for j in range(cols):
            if board[i, j] == 1:
                pygame.draw.rect(
                    screen,
                    cell_color,
                    (j * cell_size, i * cell_size, cell_size, cell_size),
                )

def main():
    global game_board
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        game_board = update_board(game_board)
        draw_board(game_board)
        pygame.display.flip()
        time.sleep(0.1)

    pygame.quit()

if __name__ == "__main__":
    main()
