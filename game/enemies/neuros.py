import pygame
import random

from game.entities import Entity
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
        self.ai_state = "sabotage"
        self.shielded = False
        self.hits_taken = 0
        self.speed = 0
        self.minions = []
        self.timer = 0
        self.action_cooldown = 0
        self.text_timer = 0
        self.text_duration = 3.0
        self.current_text = ""
        self.detection_range = 500
        self.death_executed = False
        self.apply_gravity = False
        self.heal_cooldown = 0.0
        self.walking = 0
        self.set_phase_stats(1)

    def set_phase_stats(self, phase):
        config = self.phase_configs[phase]
        self.max_health = config["health"]
        self.health = self.max_health
        self.speed = config["speed"]

    def update(self, level, dt):
        if self.health <= 0:
            self.enter_next_phase()

        self.velocity.y = 0

        if self.velocity.x > 0:
            self.facing_right = True
        elif self.velocity.x < 0:
            self.facing_right = False

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

        if self.phase == 1:
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

    # === Phase 1 ===
    def phase_1(self, dt):
        rnd_phase = random.randint(0, 20)
        if self.action_cooldown == 0 and self.walking == 0:
            if self.between(0, 4, rnd_phase):
                self.speak("Analyzing human behavior...")
                self.action_cooldown = 1.0
            elif self.between(5, 5, rnd_phase):
                self.speak("Are you afraid of me, human?")
                self.action_cooldown = 0.1
                self.walking = 2.0
            elif self.between(6, 16, rnd_phase):
                self.speak("")
                self.action_cooldown = 0.1
                self.walking = 1.5
            elif self.between(17, 18, rnd_phase):
                self.summon_drones()
                self.action_cooldown = 4.5
            elif self.between(19, 20, rnd_phase) and self.heal_cooldown == 0 and self.health != self.max_health:
                self.heal_self(3)
                self.action_cooldown = 2.5
                self.heal_cooldown = 10.0
        if self.walking > 0:
            self.move_towards_player(dt)

    # === Phase 2 ===
    def phase_2(self, dt):
        rnd_phase = random.randint(0, 20)
        if self.action_cooldown == 0 and self.walking == 0:
            if self.between(0, 3, rnd_phase):
                self.speak("Analyzing human behavior...")
                self.action_cooldown = 1.0
            elif self.between(4, 4, rnd_phase):
                self.speak("Are you afraid of me, human?")
                self.action_cooldown = 0.1
                self.walking = 2.0
            elif self.between(5, 12, rnd_phase):
                self.speak("")
                self.action_cooldown = 0.1
                self.walking = 1.5
            elif self.between(13, 15, rnd_phase):
                self.summon_drones()
                self.action_cooldown = 4.0
            elif self.between(16, 16, rnd_phase):
                self.deploy_emp_radars()
                self.action_cooldown = 5.0
            elif self.between(17, 17, rnd_phase) and self.heal_cooldown == 0 and self.health != self.max_health:
                self.heal_self(5)
                self.action_cooldown = 4.0
                self.heal_cooldown = 20.0
            elif self.between(18, 20, rnd_phase) and self.heal_cooldown == 0 and self.health != self.max_health:
                self.heal_self(3)
                self.action_cooldown = 2.0
                self.heal_cooldown = 10.0
        if self.walking > 0:
            self.move_towards_player(dt)

    # === Phase 3 ===
    def phase_3(self, dt):
        rnd_phase = random.randint(0, 20)
        if self.action_cooldown == 0 and self.walking == 0:
            if self.between(0, 1, rnd_phase):
                self.speak("Analyzing human behavior...")
                self.action_cooldown = 0.8
            elif self.between(2, 2, rnd_phase):
                self.speak("Are you afraid of me, human?")
                self.action_cooldown = 0.1
                self.walking = 2.0
            elif self.between(3, 10, rnd_phase):
                self.speak("")
                self.action_cooldown = 0.1
                self.walking = 1.5
            elif self.between(11, 14, rnd_phase):
                self.summon_drones()
                self.action_cooldown = 3.5
            elif self.between(15, 16, rnd_phase):
                self.deploy_emp_radars()
                self.action_cooldown = 4.5
            elif self.between(17, 17, rnd_phase) and self.heal_cooldown == 0 and self.health != self.max_health:
                self.heal_self(5)
                self.action_cooldown = 4.0
                self.heal_cooldown = 16.0
            elif self.between(18, 20, rnd_phase) and self.heal_cooldown == 0 and self.health != self.max_health:
                self.heal_self(3)
                self.action_cooldown = 2.0
                self.heal_cooldown = 8.0
        if self.walking > 0:
            self.move_towards_player(dt)

    def move_towards_player(self, dt):
        direction = self.player.rect.centerx - self.rect.centerx
        if direction > 0:
            self.velocity.x = self.speed * dt
        elif direction < 0:
            self.velocity.x = -self.speed * dt

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
        self.health += min((self.max_health - self.health), amt)
        self.speak("Defragmenting system. Optimization complete.")
        
    def summon_drones(self):
        if len(self.minions) < 5:
            pos = (self.rect.centerx + random.randint(-40, 40), self.rect.y)
            drone = Drone(pos[0], pos[1], "assets/characters/drone.png", "assets/characters/drone.json",
                          self.player, self.level, self.sound_manager)
            self.minions.append(drone)
            self.level.enemies.add(drone)
            self.speak("Deploying additional units.")

    def deploy_emp_radars(self):
        if len(self.minions) < 3:
            pos = (self.rect.centerx + random.randint(-100, 100), self.rect.top - 40)
            radar = EMP_Radar(pos[0], pos[1], self.level)
            self.minions.append(radar)
            self.level.enemies.add(radar)
            self.player.abilities_blocked = True

            self.speak("EMP field active.")

    def shoot_lasers(self):
        self.speak("Firing precision beams.")

    def shield_self(self):
        if self.hits_taken >= 3 and not self.shielded:
            self.shielded = True
            self.speak("Defensive matrix online.")
            self.timer = 5.0
            self.ai_state = "shielded"

    def world_hack(self):
        effect = random.choice(["gravity", "controls", "glitch"])
        if effect == "gravity":
            self.level.flip_gravity()
            self.speak("Gravity systems compromised.")
        elif effect == "controls":
            self.player.invert_controls()  # Needs to be implemented in Player
            self.speak("Control interface hacked.")
        elif effect == "glitch":
            self.speak("Reality matrix destabilized.")
            print("Visual glitch placeholder.")

    def fast_dash(self):
        direction = pygame.Vector2(self.player.rect.center) - self.rect.center
        direction.normalize_ip()
        self.velocity.x = direction * self.speed * 2

    def slow_time(self):
        self.level.engine.fps = 30  # Should reset externally
        self.speak("Temporal manipulation active.")
        self.timer = 3.0

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
            self.level.engine.menu.open_menu(MenuState.COMPLETE, self.level.engine)
        super().eliminate()

    def render(self, screen, camera):
        super().render(screen, camera)
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

    def between(self, x,y,z):
        return (x <= z <= y or y <= z <= x)