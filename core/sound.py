import pygame
import json
import os

class SoundManager:
    def __init__(self, music_volume=1, sfx_volume=1):
        pygame.mixer.init()
        self.music_volume = music_volume
        self.sfx_volume = sfx_volume
        self.loaded_sounds = {}
        self.volume_factor_music = 0.5
        self.volume_factor_sfx = 0.8

        with open("assets/sfx/sfx.json") as f:
            self.sfx_map = json.load(f)

    def sound_path(self,key):
        return f"assets/sfx/{self.sfx_map[key]}"

    def play_music(self, ):
        pygame.mixer.music.load(self.sound_path("main_theme"))
        pygame.mixer.music.set_volume(self.music_volume * self.volume_factor_music)
        pygame.mixer.music.play(-1)

    def set_music_volume(self, volume):
        self.music_volume = volume
        pygame.mixer.music.set_volume(volume)

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

    def set_sfx_volume(self, volume):
        self.sfx_volume = volume
        for sfx in self.loaded_sounds.values():
            sfx.set_volume(volume * self.volume_factor_sfx)
