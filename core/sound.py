# sound.py
import pygame
import json
from core.settings import Settings

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.settings = Settings()
        self.music_volume = self.settings.get("volume", "music")
        self.sfx_volume = self.settings.get("volume", "sfx")
        self.loaded_sounds = {}
        self.volume_factor_music = 0.5
        self.volume_factor_sfx = 0.8

        with open("assets/sfx/sfx.json") as f:
            self.sfx_map = json.load(f)

    def sound_path(self, key):
        return f"assets/sfx/{self.sfx_map[key]}"

    def play_music(self):
        pygame.mixer.music.load(self.sound_path("main_theme"))
        pygame.mixer.music.set_volume(self.music_volume * self.volume_factor_music)
        pygame.mixer.music.play(-1)

    def set_music_volume(self, volume):
        self.music_volume = volume
        pygame.mixer.music.set_volume(volume * self.volume_factor_music)

    def load_sound(self, key):
        path = self.sfx_map[key]
        if path not in self.loaded_sounds:
            sound = pygame.mixer.Sound(self.sound_path(key))
            sound.set_volume(self.sfx_volume * self.volume_factor_sfx)
            self.loaded_sounds[path] = sound
        return self.loaded_sounds[path]

    def play_sfx(self, key):
        sound = self.load_sound(key)
        if sound:
            sound.play()

    def stop_sfx(self, key):
        sound = self.load_sound(key)
        if sound:
            sound.stop()

    def set_sfx_volume(self, volume):
        self.sfx_volume = volume
        for sfx in self.loaded_sounds.values():
            sfx.set_volume(volume * self.volume_factor_sfx)

    def save_volume(self):
        self.settings.set("volume", "music", self.music_volume)
        self.settings.set("volume", "sfx", self.sfx_volume)