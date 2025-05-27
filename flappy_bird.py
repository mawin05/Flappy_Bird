import pygame
import random
import os

from pygame.math import VectorElementwiseProxy

WINDOW_HEIGHT = 750
WINDOW_WIDTH = 550
BACKGROUND_IMG = pygame.image.load(os.path.join("images", "background.png"))


class Fish:
    def __init__(self):
        self.x_position = 50
        self.y_position = WINDOW_HEIGHT / 3
        self.image = pygame.image.load(os.path.join("images", "flappy.png"))
        self.velocity = 0
        self.tick_count = 0
        self.alive = True

    def jump(self):
        self.velocity = -10.5
        self.tick_count = 0

    def move(self):
        self.tick_count += 1
        d = self.velocity * self.tick_count + 1.5 * self.tick_count ** 2

        if d >= 16:
            d = 16

        if d < 0:
            d -= 2

        self.y_position += d

    def draw(self, win):
        win.blit(self.image, (self.x_position, self.y_position))

    def get_mask(self):
        return pygame.mask.from_surface(self.image)

    def check_base_collision(self, base):
        return self.y_position + self.image.get_height() >= base.y_position

    def check_pipe_collision(self, pipe):
        fish_mask = self.get_mask()
        pipe_mask = pipe.get_mask()
        offset = (pipe.x_position - self.x_position, pipe.y_position - self.y_position)
        return fish_mask.overlap(pipe_mask, offset)


class Pipe:
    GAP = 200

    def __init__(self, x):
        self.x_position = x
        self.image = pygame.image.load(os.path.join("images", "double_sided_pipe.png"))
        self.y_position = random.randint(1, 300)
        self.y_position -= 450
        self.velocity = 5

    def move(self):
        self.x_position -= self.velocity

    def draw(self, win):
        win.blit(self.image, (self.x_position, self.y_position))

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Base:
    def __init__(self):
        self.image = pygame.image.load(os.path.join("images", "base.png"))
        self.x_position = 0
        self.y_position = WINDOW_HEIGHT - self.image.get_height()
        self.velocity = 5

    def draw(self, win):
        win.blit(self.image, (self.x_position, self.y_position))


class Game:
    BACKGROUND_IMG = pygame.image.load(os.path.join("images", "background.png"))

    def __init__(self):
        pygame.font.init()
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.fish = Fish()
        self.pipes = [Pipe(WINDOW_WIDTH)]
        self.base = Base()
        self.clock = pygame.time.Clock()
        self.score = 0

        self.last_time = 0
        self.interval = 3000

        self.runs = True
        self.playing = True

    def get_state(self):
        pipe = self.pipes[0]
        return [
            self.fish.y_position,
            self.fish.velocity,
            pipe.x_position - self.fish.x_position,
            pipe.y_position + pipe.image.get_height(),  # dolna krawędź górnej rury
            pipe.y_position + Pipe.GAP + pipe.image.get_height()  # górna krawędź dolnej rury
        ]

    def restart(self):
        self.fish = Fish()
        self.pipes.clear()
        self.pipes.append(Pipe(WINDOW_WIDTH))
        self.score = 0
        self.last_time = pygame.time.get_ticks()
        self.playing = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.runs = False

            if event.type == pygame.KEYDOWN:
                if self.playing:
                    if event.key == pygame.K_SPACE:
                        self.fish.jump()
                else:
                    if event.key == pygame.K_SPACE:
                        self.restart()
                    else:
                        self.runs = False

    def update(self):
        if not self.playing:
            return

        self.clock.tick(30)

        self.fish.move()

        if self.fish.check_base_collision(self.base):
            self.playing = False

        current_time = pygame.time.get_ticks()

        if current_time - self.last_time > self.interval:
            new_pipe = Pipe(WINDOW_WIDTH)
            self.pipes.append(new_pipe)
            self.last_time = current_time

        to_remove = []
        for pipe in self.pipes:
            pipe.move()
            if pipe.x_position + pipe.image.get_width() < 0:
                to_remove.append(pipe)

            if self.fish.check_pipe_collision(pipe):
                self.playing = False

            if (pipe.x_position + pipe.image.get_width()) == self.fish.x_position:
                self.score += 1

        for pipe in to_remove:
            self.pipes.remove(pipe)

        print(self.pipes)

    def draw(self):
        self.window.blit(BACKGROUND_IMG, (0, 0))
        for pipe in self.pipes:
            pipe.draw(self.window)
        self.base.draw(self.window)
        self.fish.draw(self.window)
        font = pygame.font.SysFont("Arial", 32)
        text_surface = font.render(f"Score: {self.score}", True, (255, 255, 255))
        text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.window.blit(text, (WINDOW_WIDTH - 150, 30))
        pygame.display.update()

    def game_loop(self):
        while self.runs:
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.game_loop()
