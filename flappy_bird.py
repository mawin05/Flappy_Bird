import pygame
import random
import os

from pygame.math import VectorElementwiseProxy

WINDOW_HEIGHT = 750
WINDOW_WIDTH = 550
BACKGROUND_IMG = pygame.image.load(os.path.join("images", "background.png"))


class Fish:
    def __init__(self):
        self.x_position = 0
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


class Pipe:
    GAP = 200
    def __init__(self, x):
        self.x_position = x
        self.image = pygame.image.load(os.path.join("images","double_sided_pipe.png"))
        self.y_position = random.randint(1, 300)
        self.y_position -= 400
        self.velocity = 5


    def move(self):
        self.x_position -= self.velocity


    def draw(self, win):
        win.blit(self.image, (self.x_position, self.y_position))


def draw_window(win, fish, pipes):
    win.blit(BACKGROUND_IMG, (0,0))
    fish.draw(win)
    for pipe in pipes:
        pipe.draw(win)
    pygame.display.update()

def main():
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    fish = Fish()
    pipes = []
    pipe = Pipe(WINDOW_WIDTH)
    pipes.append(pipe)
    clock = pygame.time.Clock()

    last_time = 0
    interval = 3000

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

        current_time = pygame.time.get_ticks()

        if current_time - last_time > interval:
            new_pipe = Pipe(WINDOW_WIDTH)
            pipes.append(new_pipe)
            last_time = current_time
            print("nowa rura")

        to_remove = []
        for pipe in pipes:
            pipe.move()
            if pipe.x_position + pipe.image.get_width() < 0:
                to_remove.append(pipe)

        for pipe in to_remove:
            pipes.remove(pipe)

        to_remove.clear()

        draw_window(window, fish, pipes)

    pygame.quit()
    quit()

main()