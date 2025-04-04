import pygame
import random
import math

from game.entities import Entity
from game.enemies import Battery
from game.enemies import Drone
from game.enemies import EMP_Radar
from game.enemies.enemy_registry import register_enemy
from game.menu.menu_state import MenuState

@register_enemy("neuros")
class Neuros(Entity):
    def __init__(self, x, y, sprite_path, json_path, player, level, sound_manager):
        super().__init__(x, y, sprite_path, json_path, level, sound_manager)
        self.player = player
        self.level = level

        self.phase_configs = {
            1: {"health": 16, "speed": 64},
            2: {"health": 20, "speed": 96},
            3: {"health": 32, "speed": 144}
        }

        self.phase = 1
        self.shielded = False
        self.slow_timer = 0
        self.hits_taken = 0
        self.speed = 0
        self.minions = []
        self.shield_timer = 0
        self.action_cooldown = 0
        self.text_timer = 0
        self.text_duration = 3.0
        self.current_text = ""
        self.detection_range = 500
        self.death_executed = False
        self.apply_gravity = False
        self.beam_duration = 1.0
        self.beam_timer = 0
        self.beam_start = None
        self.beam_end = None
        self.heal_cooldown = 0.0
        self.walking = 2.0
        self.laser_damage = 1
        self.damage = 0
        self.firing_laser = False
        self.kb_x = 1
        self.kb_y = 1
        self.set_phase_stats(self.phase)

        self.hover_timer = 0.0
        self.hover_amplitude = 5  # pixel height of wave
        self.hover_speed = 5  # how fast the wave moves
        self.base_y = y  # original Y-position

    def set_phase_stats(self, phase):
        self.face_player()
        config = self.phase_configs[phase]
        self.max_health = config["health"]
        self.health = self.max_health
        self.speed = config["speed"]
        if self.phase == 3:
            self.beam_duration = 0.75
            self.laser_damage = 2

    def update(self, level, dt):
        if self.health <= 0:
            self.enter_next_phase()

        frames = self.sprites.get(self.state, [])
        if frames and self.sprite_index >= len(frames) - 1:
            if self.state != "idle":
                self.set_state("idle")

        # Hovering effect using sine wave
        self.hover_timer += dt * self.hover_speed
        hover_offset = math.sin(self.hover_timer) * self.hover_amplitude
        self.rect.y = self.base_y + hover_offset

        self.velocity.y = 0

        super().update(level, dt)

        self.velocity.x = 0

        self.update_text(dt)
        if self.action_cooldown > 0:
            self.action_cooldown -= dt
            if self.action_cooldown < 0:
                self.action_cooldown = 0

        if self.heal_cooldown > 0:
            self.heal_cooldown -= dt
            if self.heal_cooldown < 0:
                self.heal_cooldown = 0

        if self.walking > 0:
            self.walking -= dt
            if self.walking < 0:
                self.walking = 0

        if self.shield_timer > 0:
            self.shield_timer -= dt
            if self.shield_timer < 0:
                self.shield_timer = 0
        else:
            self.shielded = False

        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer < 0:
                self.slow_timer = 0
        else:
            self.level.engine.slow = False

        if self.beam_timer > 0:
            self.beam_timer -= dt
            if self.beam_timer < 0:
                self.beam_timer = 0
        elif self.firing_laser:
            self.shoot_lasers()
            self.firing_laser = False
            return
        
        for m in self.minions:
            if m.health == 0:
                self.minions.remove(m)

        if self.phase == 1:
            #self.testphase(dt)
            self.phase_1(dt)
        elif self.phase == 2:
            self.phase_2(dt)
        elif self.phase == 3:
            self.phase_3(dt)

    def update_text(self, dt):
        if self.text_timer > 0:
            self.text_timer -= dt
            if self.text_timer <= 0:
                self.current_text = ""

    def speak(self, text, duration = 3.0):
        self.current_text = text
        self.text_timer = duration

    def testphase(self, dt):
        if self.action_cooldown == 0:
            self.summon_batteries(3)
            self.action_cooldown = 2.0
        #self.phase_1(dt)

    def flip_gravity(self):
        pass

    # === Phase 1 ===
    def phase_1(self, dt):
        rnd_phase = random.randint(0, 100)
        if self.action_cooldown == 0 and self.walking == 0:
            if self.between(0, 16, rnd_phase):
                self.speak("Analyzing human behavior...")
                self.face_player()
                self.action_cooldown = 1.0
            elif self.between(17, 20, rnd_phase):
                self.speak("Are you afraid of me, human?")
                self.face_player()
                self.action_cooldown = 0.1
                self.walking = 2.0
            elif self.between(21, 56, rnd_phase):
                self.speak("")
                self.face_player()
                self.action_cooldown = 0.1
                self.walking = 1.0
            elif self.between(57, 72, rnd_phase):
                self.action_cooldown = 2.9
                self.face_player()
                self.aim()
            elif self.between(73, 78, rnd_phase):
                self.summon_drones()
                self.action_cooldown = 2.9
            elif self.between(79, 80, rnd_phase):
                self.summon_batteries(1)
                self.action_cooldown = 2.8
            elif self.between(81, 100, rnd_phase) and self.heal_cooldown == 0 and self.health != self.max_health:
                self.heal_self(3)
                self.action_cooldown = 2.5
                self.heal_cooldown = 10.0
        if self.walking > 0:
            self.move_towards_player(dt)

    # === Phase 2 ===
    def phase_2(self, dt):
        rnd_phase = random.randint(0, 100)
        if self.action_cooldown == 0 and self.walking == 0:
            if self.between(0, 12, rnd_phase):
                self.speak("Analyzing human behavior...")
                self.action_cooldown = 0.8
            elif self.between(13, 15, rnd_phase):
                self.speak("Are you afraid of me, human?")
                self.action_cooldown = 0.1
                self.face_player()
                self.walking = 2.0
            elif self.between(16, 48, rnd_phase):
                self.speak("")
                self.action_cooldown = 0.1
                self.face_player()
                self.walking = 1.5
            elif self.between(49, 52, rnd_phase):
                self.summon_drones()
                self.action_cooldown = 2.5
            elif self.between(53, 56, rnd_phase):
                self.summon_batteries(2)
                self.action_cooldown = 2.6
            elif self.between(57, 62, rnd_phase):
                self.deploy_emp_radars()
                self.action_cooldown = 2.2
            elif self.between(62, 67, rnd_phase):
                self.shield_self()
                self.action_cooldown = 3.2
            elif self.between(68, 88, rnd_phase):
                self.action_cooldown = 2.2
                self.face_player()
                self.aim()
            elif self.between(89, 95, rnd_phase) and self.heal_cooldown == 0 and self.health != self.max_health:
                self.heal_self(3)
                self.action_cooldown = 2.1
                self.heal_cooldown = 6.4
            elif self.between(96, 100, rnd_phase) and self.heal_cooldown == 0 and self.health != self.max_health:
                self.heal_self(5)
                self.action_cooldown = 2.6
                self.heal_cooldown = 14.0
        if self.walking > 0:
            self.move_towards_player(dt)

    # === Phase 3 ===
    def phase_3(self, dt):
        rnd_phase = random.randint(0, 100)
        if self.action_cooldown == 0 and self.walking == 0:
            if self.between(0, 3, rnd_phase):
                self.speak("Analyzing human behavior...")
                self.action_cooldown = 0.8
            elif self.between(4, 4, rnd_phase):
                self.speak("Are you afraid of me, human?")
                self.action_cooldown = 0.1
                self.face_player()
                self.walking = 1.5
            elif self.between(5, 20, rnd_phase):
                self.speak("")
                self.action_cooldown = 0.1
                self.face_player()
                self.walking = 1.0
            elif self.between(21, 32, rnd_phase):
                self.summon_drones()
                self.action_cooldown = 2.0
            elif self.between(33, 38, rnd_phase):
                self.summon_batteries(4)
                self.action_cooldown = 2.5
            elif self.between(39, 44, rnd_phase):
                self.deploy_emp_radars()
                self.action_cooldown = 1.5
            elif self.between(45, 49, rnd_phase):
                self.shield_self()
                self.action_cooldown = 3.0
            elif self.between(50, 78, rnd_phase):
                self.face_player()
                self.aim()
                self.action_cooldown = 2.0
            elif self.between(79, 83, rnd_phase):
                self.slow_time()
                self.action_cooldown = 2.0
            elif self.between(84, 89, rnd_phase):
                self.world_hack()
                self.action_cooldown = 2.5
            elif self.between(90, 100, rnd_phase) and self.heal_cooldown == 0 and self.health != self.max_health:
                self.heal_self(6)
                self.heal_cooldown = 10.0
                self.action_cooldown = 1.5
        if self.walking > 0:
            self.move_towards_player(dt)

    def move_towards_player(self, dt):
        if self.facing_right:
            self.velocity.x += self.speed * dt
        else:
            self.velocity.x -= self.speed * dt

    def enter_next_phase(self):
        self.phase += 1
        if self.phase > 3:
            self.speak("NOOOOOOOOOOOOOO!")
            self.eliminate()
        self.set_phase_stats(self.phase)
        self.stun = 20
        self.hits_taken = 0

        if self.phase == 2:
            self.speak("Analysis complete. Initiating countermeasures.")
        elif self.phase == 3:
            self.speak("You are an annoyance. Termination protocol engaged.")

    ### Attacks ###
    def heal_self(self, amt):
        self.set_state("heal")
        self.speak("Defragmenting system. Optimization complete.")
        self.sound_manager.play_sfx("boss_healing")
        self.health += min((self.max_health - self.health), amt)
        
    def summon_drones(self):
        self.set_state("summon_enemy")
        if len(self.minions) < 5:
            pos = (self.rect.centerx + random.randint(-20, 20), self.rect.y)
            drone = Drone(pos[0], pos[1], "assets/characters/drone.png", "assets/characters/drone.json",
                          self.player, self.level, self.sound_manager)
            self.minions.append(drone)
            self.level.enemies.add(drone)
            self.speak("Deploying additional unit.")
        
    def summon_batteries(self, amt):
        self.set_state("summon_enemy")
        if len(self.minions) < 8:
            for a in range(amt):
                pos = [self.rect.centerx + random.randint(-40, 40), self.rect.centery]
                battery = Battery(pos[0], pos[1], "assets/characters/battery.png", "assets/characters/battery.json",
                                self.player, self.level, self.sound_manager)
                self.minions.append(battery)
                self.level.enemies.add(battery)
                self.speak("Deploying destruction units.")

    def deploy_emp_radars(self):
        self.set_state("summon_enemy")
        self.sound_manager.play_sfx("glitch")
        if len(self.minions) < 6:
            pos = (self.rect.centerx + random.randint(-40, 40), self.rect.top + 20)
            radar = EMP_Radar(pos[0], pos[1], self.level, self.player)
            self.minions.append(radar)
            self.level.enemies.add(radar)
            self.speak("EMP field active.")

    def aim(self):
        self.speak("Firing precision beam.")
        self.firing_laser = True
        self.beam_timer = self.beam_duration
        self.beam_start = self.rect.center
        self.beam_end = self.find_wall_in_direction()

    def shoot_lasers(self):
        self.set_state("laser_attack")
        self.sound_manager.play_sfx("laser_gun")
        if self.player.rect.clipline(self.beam_start, self.beam_end):
            self.damage = self.laser_damage
            self.player.hit(self)

    def find_wall_in_direction(self):
        x_rise = self.player.rect.centerx - self.beam_start[0]
        y_rise = self.player.rect.centery - self.beam_start[1]
        for i in range(0, 2000):
            x = math.floor((self.beam_start[0] + x_rise * i * 0.1))
            y = math.floor((self.beam_start[1] + y_rise * i * 0.1))
            if self.level.get_tile_at(x,y):
                return [x, y]
        return self.player.rect.center

    def shield_self(self):
        self.set_state("shield")
        self.speak("Defensive matrix online.")
        self.sound_manager.play_sfx("boss_shield")
        self.shielded = True
        self.shield_timer = 5.0

    def world_hack(self):
        effect = random.choice(["gravity", "controls"])
        #effect = random.choice(["gravity", "controls", "glitch"])
        if effect == "gravity":
            self.level.flip_gravity()
            self.speak("Gravity systems compromised.")
        elif effect == "controls":
            self.player.invert_controls()  # Needs to be implemented in Player
            self.speak("Control interface hacked.")
        elif effect == "glitch":
            self.speak("Reality matrix destabilized.")
            print("Visual glitch placeholder.")

    def slow_time(self):
        self.sound_manager.play_sfx("glitch")
        self.level.engine.slow = True
        self.speak("Temporal manipulation active.")
        self.slow_timer = 2.0   #4 seconds due to slowdown 

    def hit(self, attacker, stun = 0):
        if self.shielded:
            return
        super().hit(attacker, stun)
        self.hits_taken += 1

    def eliminate(self):
        if self.phase == 3 and not self.death_executed:
            self.death_executed = True
            for minion in self.minions:
                minion.eliminate()
            self.level.engine.menu.open_menu(MenuState.COMPLETE, self.level.engine, self.level)
        super().eliminate()

    def render(self, screen, camera, debug_overlay=False):
        super().render(screen, camera, debug_overlay)
        if self.current_text:
            font = self.level.engine.font_manager
            pos = camera.apply(self)
            font.render(
                surface=screen,
                text=self.current_text,
                position=(pos[0] + self.rect.width // 2, pos[1] - 20),
                size=16,
                align_center=True,
                color=(255, 255, 255),
                alpha=255
            )
        
        # Beam (pretty)
        if self.firing_laser:
            if self.between(0, 0.1, self.beam_timer) and self.beam_start and self.beam_end:
                start = camera.apply(pygame.Rect(self.beam_start, (0, 0))).topleft
                end = camera.apply(pygame.Rect(self.beam_end, (0, 0))).topleft
                pygame.draw.line(screen, (100, 150, 255), start, end, self.level.tile_size // 4)
                pygame.draw.line(screen, (170, 200, 255), start, end, self.level.tile_size // 9)
            elif self.between(0.1, self.beam_duration, self.beam_timer) and self.beam_start and self.beam_end:
                start = camera.apply(pygame.Rect(self.beam_start, (0, 0))).topleft
                end = camera.apply(pygame.Rect(self.beam_end, (0, 0))).topleft
                pygame.draw.line(screen, (0, 0, 0), start, end, 1)

    def face_player(self):
        self.facing_right = self.rect.centerx < self.player.rect.centerx

    @staticmethod
    def between(x, y, z):
        return x <= z <= y or y <= z <= x