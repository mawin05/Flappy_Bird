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
        self.y_position = WINDOW_HEIGHT/2
        self.image = pygame.image.load(os.path.join("images","flappy.png"))
        self.velocity = 0
        self.tick_count = 0
        self.alive = True


    def jump(self):
        self.velocity = -10.5
        self.tick_count = 0

    def move(self):
        self.tick_count += 1
        d = self.velocity * self.tick_count + 1.5 * self.tick_count**2

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
        self.image = pygame.image.load(os.path.join("images","double_sided_pipe.png"))
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
        self.image = pygame.image.load(os.path.join("images","base.png"))
        self.x_position = 0
        self.y_position = WINDOW_HEIGHT-self.image.get_height()
        self.velocity = 5

    def draw(self, win):
        win.blit(self.image, (self.x_position, self.y_position))

def draw_window(win, fish, pipes, base, text):
    win.blit(BACKGROUND_IMG, (0,0))
    for pipe in pipes:
        pipe.draw(win)
    base.draw(win)
    fish.draw(win)
    win.blit(text, (WINDOW_WIDTH-150, 30))
    pygame.display.update()

def main():
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    fish = Fish()
    pipes = []
    pipe = Pipe(WINDOW_WIDTH)
    pipes.append(pipe)
    base = Base()
    clock = pygame.time.Clock()
    score = 0

    last_time = 0
    interval = 3000

    pygame.font.init()
    font = pygame.font.SysFont("Arial", 32)
    text_surface = font.render(f"Score: {score}", True, (255, 255, 255))

    runs = True
    while runs:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                runs = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    fish.jump()

        fish.move()

        if fish.check_base_collision(base):
            runs = False

        current_time = pygame.time.get_ticks()

        if current_time - last_time > interval:
            new_pipe = Pipe(WINDOW_WIDTH)
            pipes.append(new_pipe)
            last_time = current_time

        to_remove = []
        for pipe in pipes:
            pipe.move()
            if pipe.x_position + pipe.image.get_width() < 0:
                to_remove.append(pipe)

            if fish.check_pipe_collision(pipe):
                runs = False

            if (pipe.x_position + pipe.image.get_width()) == fish.x_position:
                score += 1
                text_surface = font.render(f"Score: {score}", True, (255, 255, 255))

        for pipe in to_remove:
            pipes.remove(pipe)

        to_remove.clear()

        draw_window(window, fish, pipes, base, text_surface)

    pygame.quit()
    quit()

main()