import pygame
import random
import os
import math
from Agent import Agent

from pygame.math import VectorElementwiseProxy

WINDOW_HEIGHT = 750
WINDOW_WIDTH = 550
BACKGROUND_IMG = pygame.image.load(os.path.join("images", "background.png"))


class Fish:
    def __init__(self):
        self.x_position = 50
        self.y_position = WINDOW_HEIGHT / 3
        self.image = pygame.image.load(os.path.join("images", "flappy.png"))
        self.velocity = -18
        self.acceleration = 2
        self.alive = True

    def jump(self):
        self.velocity = -18

    def move(self):
        self.y_position += self.velocity
        self.velocity += self.acceleration

        if self.velocity >= 20:
            self.velocity = 20

    def draw(self, win):
        win.blit(self.image, (self.x_position, self.y_position))

    def get_mask(self):
        return pygame.mask.from_surface(self.image)

    def check_base_collision(self, base):
        return self.y_position + self.image.get_height() >= base.y_position

    def check_pipe_collision(self, pipe):
        fish_mask = self.get_mask()
        upper_pipe_mask = pipe.get_upper_mask()
        bottom_pipe_mask = pipe.get_bottom_mask()
        upper_offset = (pipe.x_position - self.x_position, pipe.upper_y_position - self.y_position)
        bottom_offset = (pipe.x_position - self.x_position, pipe.bottom_y_position - self.y_position)
        return fish_mask.overlap(upper_pipe_mask, upper_offset) or fish_mask.overlap(bottom_pipe_mask, bottom_offset)

    def check_roof_collision(self):
        return self.y_position <= 0

class Pipe:
    GAP = 220
    UPPER_LIMIT = 50    # górna granica ograniczająca pozycję rury
    BOTTOM_LIMIT = 320  # dolna granica

    def __init__(self, x):
        self.x_position = x
        self.bottom_image = pygame.image.load(os.path.join("images", "pipe.png"))
        self.upper_image = pygame.transform.flip(self.bottom_image, False, True)
        height = self.upper_image.get_height()
        self.upper_y_position = random.randint(Pipe.UPPER_LIMIT-height, Pipe.BOTTOM_LIMIT-height)
        self.bottom_y_position = self.upper_y_position + Pipe.GAP + self.upper_image.get_height()
        self.velocity = 5

    def move(self):
        self.x_position -= self.velocity

    def draw(self, win):
        win.blit(self.upper_image, (self.x_position, self.upper_y_position))
        win.blit(self.bottom_image, (self.x_position, self.bottom_y_position))

    def get_upper_mask(self):
        return pygame.mask.from_surface(self.upper_image)

    def get_bottom_mask(self):
        return pygame.mask.from_surface(self.bottom_image)

    def get_borders(self):
        top_pipe_border = self.upper_y_position + self.upper_image.get_height()
        bottom_pipe_border = self.bottom_y_position
        return top_pipe_border, bottom_pipe_border


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
        self.interval = 2750

        self.runs = True
        self.playing = True

        self.agent = Agent(input_dim=4, output_dim=2)
        self.previous_state = self.get_state()
        self.previous_action = None

    def get_state(self):
        pipe = self.closestPipe() # rura, która jest najbliżej, ale której nie minął agent
        top, _ = pipe.get_borders()
        return [
            self.fish.y_position, # wysokość agenta
            self.fish.velocity, # prędkość agenta
            pipe.x_position - self.fish.x_position, # odległość między agenetem a najbliższą rurą
            top - self.fish.y_position,  # różnica wysokości między agentem a dolną krawędzią górnej rury
        ]
        # górna krawędź dolnej rury się nie przyda, ponieważ jest to rzecz zależna od
        # dolnej krawędzi górnej rury, jest to więc dwukrotnie przekazywana ta sama informacja

    def closestPipe(self):
        # funkcja ta zwraca najbliższą rurę, której agent jeszcze nie minął
        # oryginalnie zwracała zawsze pierwszą rurę, lecz był krótki moment kiedy agent mijał
        # pierwszą rurę i czekał aż ona zniknie z ekranu by dostać informacje o rurze przed sobą
        # tu ten problem jest rozwiązany, w momencie w którym agent nie może zginąć przez 1 rurę,
        # dostaje informacje o położeniu kolejnej
        pipeWidth = self.pipes[0].upper_image.get_width()
        for pipe in self.pipes:
            if pipe.x_position - self.fish.x_position > -pipeWidth:
                return pipe
        return self.pipes[0]

    def restart(self):
        self.fish = Fish()
        self.pipes.clear()
        self.pipes.append(Pipe(WINDOW_WIDTH))
        self.score = 0
        self.last_time = pygame.time.get_ticks()
        self.playing = True
        self.previous_state = self.get_state()
        self.previous_action = None

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
        current_state = self.get_state()

        action = self.agent.select_action(current_state)
        if action == 1:
            self.fish.jump()

        self.fish.move()

        # defaultowo agent dostaje trochę punktów za przetrwanie
        reward = 0.1
        done = False

        if self.fish.check_base_collision(self.base) or self.fish.check_roof_collision():
            # jeżeli agent uderzy w barierkę dostaje dużą karę
            reward = -5
            done = True
            self.playing = False

        current_time = pygame.time.get_ticks()

        if current_time - self.last_time > self.interval:
            new_pipe = Pipe(WINDOW_WIDTH)
            self.pipes.append(new_pipe)
            self.last_time = current_time

        to_remove = []
        for pipe in self.pipes:
            pipe.move()
            if pipe.x_position + pipe.upper_image.get_width() < 0:
                to_remove.append(pipe)

            if self.fish.check_pipe_collision(pipe):
                # jeżeli agent uderzy w rurę, dostaje karę, która zależy od odległości jego od środka szpary

                f_x, f_y = self.fish.x_position, self.fish.y_position + self.fish.image.get_height() / 2
                p_x, p_y = pipe.x_position + pipe.upper_image.get_width(), pipe.get_borders()[0] + pipe.GAP / 2

                reward = -1 + -4 * math.sqrt((f_x - p_x) ** 2 + (f_y - p_y) ** 2) / WINDOW_HEIGHT
                print(reward)
                done = True
                self.playing = False

            if (pipe.x_position + pipe.upper_image.get_width()) == self.fish.x_position:
                # jeżeli agent przejdzie szparę, dostaje dużą nagrodę
                self.score += 1
                reward = 5

        for pipe in to_remove:
            self.pipes.remove(pipe)

        # dodanie wpisu stanu, akcji i jej konsekwencji do bufora pamięci oraz trenowanie agenta
        if self.previous_action is not None:
            self.agent.replay_buffer.push(
                (self.previous_state,
                self.previous_action,
                current_state,
                reward,
                done)
            )
            self.agent.train()

        self.previous_state = current_state
        self.previous_action = action

        #print(self.pipes)
        #print(self.get_state())

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
        #pygame.draw.line(self.window, (255, 0, 0), (0, 350), (WINDOW_WIDTH, 350), 2)
        pygame.display.update()

    def game_loop(self):
        while self.runs:
            if not self.playing:
                self.restart()
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.game_loop()
