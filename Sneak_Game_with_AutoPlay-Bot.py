import pygame
import sys
import math
import random
from collections import deque

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Snake Auto-Bot")

# Colors
BACKGROUND = (10, 5, 25)  # Deep space blue
GRID_COLOR = (30, 20, 50)  # Dark grid color
SNAKE_COLOR = (0, 200, 255)  # Cyan
SNAKE_GLOW = (100, 255, 255)  # Bright cyan glow
FOOD_COLOR = (255, 50, 150)  # Pink
FOOD_GLOW = (255, 150, 200)  # Pink glow
UI_COLOR = (200, 220, 255)  # Light blue for text
UI_ACCENT = (100, 150, 255)  # Blue accent

# Game settings
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE
SNAKE_SPEED = 12

# Fonts
title_font = pygame.font.SysFont("Arial", 48, bold=True)
ui_font = pygame.font.SysFont("Arial", 32)
small_font = pygame.font.SysFont("Arial", 24)


class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.length = 3
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.score = 0
        self.grow_to = 3
        self.path = deque()

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        head = self.get_head_position()
        x, y = self.direction
        new_position = (((head[0] + x) % GRID_WIDTH), ((head[1] + y) % GRID_HEIGHT))

        if new_position in self.positions[1:]:
            return False  # Game over

        self.positions.insert(0, new_position)

        if len(self.positions) > self.grow_to:
            self.positions.pop()

        return True

    def draw(self, surface):
        for i, pos in enumerate(self.positions):
            # Create a glowing effect for the snake
            rect = pygame.Rect((pos[0] * CELL_SIZE, pos[1] * CELL_SIZE), (CELL_SIZE, CELL_SIZE))

            # Draw glow
            if i == 0:  # Head has stronger glow
                glow_radius = 10
                glow_surface = pygame.Surface((CELL_SIZE + glow_radius * 2, CELL_SIZE + glow_radius * 2),
                                              pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (*SNAKE_GLOW, 80),
                                 (0, 0, CELL_SIZE + glow_radius * 2, CELL_SIZE + glow_radius * 2), border_radius=5)
                surface.blit(glow_surface, (rect.x - glow_radius, rect.y - glow_radius))
            else:
                glow_radius = 5
                glow_surface = pygame.Surface((CELL_SIZE + glow_radius * 2, CELL_SIZE + glow_radius * 2),
                                              pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (*SNAKE_GLOW, 50),
                                 (0, 0, CELL_SIZE + glow_radius * 2, CELL_SIZE + glow_radius * 2), border_radius=3)
                surface.blit(glow_surface, (rect.x - glow_radius, rect.y - glow_radius))

            # Draw snake segment
            pygame.draw.rect(surface, SNAKE_COLOR, rect, border_radius=5)
            pygame.draw.rect(surface, UI_ACCENT, rect, 2, border_radius=5)


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))

    def draw(self, surface):
        rect = pygame.Rect((self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE), (CELL_SIZE, CELL_SIZE))

        # Draw glow
        glow_radius = 15
        glow_surface = pygame.Surface((CELL_SIZE + glow_radius * 2, CELL_SIZE + glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*FOOD_GLOW, 100),
                         (0, 0, CELL_SIZE + glow_radius * 2, CELL_SIZE + glow_radius * 2), border_radius=10)
        surface.blit(glow_surface, (rect.x - glow_radius, rect.y - glow_radius))

        # Draw food
        pygame.draw.rect(surface, FOOD_COLOR, rect, border_radius=10)
        pygame.draw.rect(surface, UI_ACCENT, rect, 2, border_radius=10)

        # Draw inner circle
        inner_rect = rect.inflate(-8, -8)
        pygame.draw.rect(surface, (255, 200, 220), inner_rect, border_radius=7)


class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.game_over = False
        self.clock = pygame.time.Clock()

    def find_path(self):
        """BFS algorithm to find path from snake head to food"""
        head = self.snake.get_head_position()
        food_pos = self.food.position

        # Don't include tail as obstacle since it will move
        obstacles = set(self.snake.positions[1:-1])

        # BFS setup
        queue = deque()
        queue.append((head, []))  # (position, path to get there)
        visited = set([head])

        # Possible moves
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        while queue:
            (x, y), path = queue.popleft()

            # Found food!
            if (x, y) == food_pos:
                return path

            # Explore neighbors
            for dx, dy in directions:
                nx, ny = (x + dx) % GRID_WIDTH, (y + dy) % GRID_HEIGHT
                if (nx, ny) not in visited and (nx, ny) not in obstacles:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(dx, dy)]))

        # If no path found, move randomly to avoid obstacles
        safe_moves = []
        for dx, dy in directions:
            nx, ny = (head[0] + dx) % GRID_WIDTH, (head[1] + dy) % GRID_HEIGHT
            if (nx, ny) not in obstacles:
                safe_moves.append((dx, dy))

        return [random.choice(safe_moves)] if safe_moves else [random.choice(directions)]

    def update(self):
        if not self.game_over:
            # Calculate path to food using BFS
            if not self.snake.path:
                self.snake.path = deque(self.find_path())

            # Follow the calculated path
            if self.snake.path:
                self.snake.direction = self.snake.path.popleft()

            # Update snake position
            if not self.snake.update():
                self.game_over = True
                return

            # Check for food collision
            if self.snake.get_head_position() == self.food.position:
                self.snake.grow_to += 1
                self.snake.score += 10
                self.food.randomize_position()

                # Make sure food doesn't appear on snake
                while self.food.position in self.snake.positions:
                    self.food.randomize_position()

    def draw(self):
        # Draw background
        screen.fill(BACKGROUND)

        # Draw grid
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y), 1)

        # Draw title
        title_text = title_font.render("SPACE SNAKE", True, UI_COLOR)
        title_rect = title_text.get_rect(center=(WIDTH // 2, 30))
        screen.blit(title_text, title_rect)

        # Draw game elements
        self.food.draw(screen)
        self.snake.draw(screen)

        # Draw score at top right
        score_text = ui_font.render(f"Score: {self.snake.score}", True, UI_COLOR)
        screen.blit(score_text, (WIDTH - score_text.get_width() - 20, 20))

        # Draw game over screen
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            game_over_text = title_font.render("GAME OVER", True, (255, 100, 100))
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 60))

            final_score = ui_font.render(f"Final Score: {self.snake.score}", True, UI_COLOR)
            screen.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, HEIGHT // 2 + 10))

            restart_text = small_font.render("Press SPACE to restart", True, UI_COLOR)
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 70))


def main():
    game = Game()

    # Add some stars to the background
    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT),
              random.random() * 2 + 0.5, random.random() * 0.5 + 0.1)
             for _ in range(100)]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_SPACE and game.game_over:
                    game = Game()  # Reset game

        # Update stars
        for i, (x, y, size, speed) in enumerate(stars):
            y = (y + speed) % HEIGHT
            stars[i] = (x, y, size, speed)

        # Draw stars
        for x, y, size, speed in stars:
            alpha = min(255, int(150 + 105 * math.sin(pygame.time.get_ticks() * 0.001 + x)))
            pygame.draw.circle(screen, (200, 220, 255, alpha), (x, y), size)

        # Update and draw game
        game.update()
        game.draw()

        pygame.display.flip()
        game.clock.tick(SNAKE_SPEED)


if __name__ == "__main__":
    main()
