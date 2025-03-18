import json

import pygame

from core.camera import Camera
from core.game_data import get_game_data
from game.background import Background
from game.levels import Level
from game.menu import Menu, MenuOptions
from game.player import Player
from game.enemy import Enemy
from core.controls import Controls
from game.enemies.enemy import Enemy
from game.user_interface import UI

class GameEngine:
    def __init__(self):
        pygame.init()

        self.native_size = get_game_data("screen_size")
        self.fps = get_game_data("fps")

        self.screen = pygame.display.set_mode(self.native_size, pygame.RESIZABLE)
        pygame.display.set_caption(get_game_data("game_title"))

        self.clock = pygame.time.Clock()
        w2, h2 = get_game_data("enemy_size")
        s2 = get_game_data("enemy_scale")

        self.current_level = 0
        self.level = Level(self.current_level)

        self.player = self.load_player()
        self.enemy = Enemy(400, 400, w2, h2, s2, self.player)

        with open("assets/background/background.json") as f:
            data = json.load(f)

        self.backgrounds = [Background(d) for d in data[::-1]]

        self.is_running = True
        self.is_menu = True

        self.menu = Menu()

        self.scaled_surface = pygame.Surface(self.native_size)
        self.camera = Camera(self.native_size[0], self.native_size[1], self.level.width, self.level.height)

        self.controls = Controls()  #   das könnte Mist sein
        self.ui = UI(self.screen)
        self.controls = self.player.controls

    def load_player(self):
        w, h = get_game_data("player_size")
        s = get_game_data("player_scale")
        x,y = self.level.spawn
        return Player(x, y, w, h, s)

    def load_next_level(self):
        self.current_level += 1
        self.level = Level(self.current_level)
        self.camera = Camera(self.native_size[0], self.native_size[1], self.level.width, self.level.height)
        self.player = self.load_player()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            self.ui.handle_events(event, self)

    def render(self):
        self.scaled_surface.fill((0, 0, 0))
        for background in self.backgrounds:
            background.render(self.scaled_surface, self.camera)
        self.level.render(self.scaled_surface, self.camera)
        self.player.render(self.scaled_surface, self.camera)
        self.enemy.render(self.scaled_surface, self.camera)

        screen_width, screen_height = self.screen.get_size()
        scale_x = screen_width / self.native_size[0]
        scale_y = screen_height / self.native_size[1]
        scale = min(scale_x, scale_y)
        new_width = int(self.native_size[0] * scale)
        new_height = int(self.native_size[1] * scale)
        scaled_surface = pygame.transform.scale(self.scaled_surface, (new_width, new_height))
        x_offset = (screen_width - new_width) // 2
        y_offset = (screen_height - new_height) // 2

        self.screen.fill((0, 0, 255))
        self.screen.blit(scaled_surface, (x_offset, y_offset))

        self.ui.render(x_offset, y_offset, new_width, new_height)

    def update(self):
        self.player.update(self.level, 1 / self.fps)
        self.enemy.update(self.level, 1 / self.fps)
        self.level.check_touch(self.player, self)
        self.camera.follow(self.player)

    def run(self):
        w, h = pygame.display.get_window_size()[0], pygame.display.get_window_size()[1]
        self.menu.update_layout(w,h)
        while self.is_running:
            self.clock.tick(self.fps)
            if self.is_menu:
                self.menu.handle_events(self)
                self.menu.render(self.screen)
            elif self.controls.is_action_active("menu"):    # Das könnte Mist sein
                self.menu.open_menu(MenuOptions.PAUSE,self)                             # das könnte MIst
            else:
                self.handle_events()
                self.update()
                self.render()
            pygame.display.flip()

        pygame.quit()
