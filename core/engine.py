import pygame
from core.game_data import get_game_data
from game.background import Background
from game.levels import Level
from game.player import Player

class GameEngine:
    def __init__(self):
        pygame.init()

        self.screen_size = get_game_data("screen_size")
        self.fps = get_game_data("fps")

        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption(get_game_data("game_title"))

        self.clock = pygame.time.Clock()
        self.player = Player(50, 50)
        self.background = Background()
        self.level = Level(0)

        self.is_running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

    def render(self):
        self.screen.fill((0, 0, 0))
        self.background.render(self.screen)
        self.level.render(self.screen)
        self.player.render(self.screen, (255, 0, 255))

    def update(self):
        self.player.update(self.level, 1/self.fps)

    def run(self):
        while self.is_running:
            self.clock.tick(self.fps)
            self.handle_events()
            self.update()
            self.render()
            pygame.display.flip()

        pygame.quit()