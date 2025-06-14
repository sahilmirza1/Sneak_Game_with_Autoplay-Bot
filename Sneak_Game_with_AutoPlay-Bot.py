import pygame
import random
import time

pygame.init()

# Window setup
width, height = 600, 400
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Auto Snake Bot")

# Colors
black = (0, 0, 0)
green = (0, 255, 0)
red   = (255, 0, 0)

# Snake settings
snake_block = 10
snake_speed = 15
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 35)

def message(msg, color):
    text = font.render(msg, True, color)
    win.blit(text, [width / 6, height / 3])

def game_loop():
    x = width / 2
    y = height / 2
    dx = 0
    dy = 0

    snake_list = []
    snake_length = 1

    food_x = round(random.randrange(0, width - snake_block) / 10.0) * 10.0
    food_y = round(random.randrange(0, height - snake_block) / 10.0) * 10.0

    game_over = False

    while not game_over:
        # Auto movement towards food
        if x < food_x:
            dx = snake_block
            dy = 0
        elif x > food_x:
            dx = -snake_block
            dy = 0
        elif y < food_y:
            dy = snake_block
            dx = 0
        elif y > food_y:
            dy = -snake_block
            dx = 0

        x += dx
        y += dy

        if x >= width or x < 0 or y >= height or y < 0:
            game_over = True

        win.fill(black)
        pygame.draw.rect(win, red, [food_x, food_y, snake_block, snake_block])

        snake_head = [x, y]
        snake_list.append(snake_head)

        if len(snake_list) > snake_length:
            del snake_list[0]

        for segment in snake_list[:-1]:
            if segment == snake_head:
                game_over = True

        for segment in snake_list:
            pygame.draw.rect(win, green, [segment[0], segment[1], snake_block, snake_block])

        pygame.display.update()

        if x == food_x and y == food_y:
            food_x = round(random.randrange(0, width - snake_block) / 10.0) * 10.0
            food_y = round(random.randrange(0, height - snake_block) / 10.0) * 10.0
            snake_length += 1

        clock.tick(snake_speed)

    message("Game Over! Press ESC to quit.", red)
    pygame.display.update()
    time.sleep(2)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()

game_loop()
