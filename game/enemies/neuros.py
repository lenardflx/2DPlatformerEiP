import pygame
import random

from game.enemies import Drone
from game.entities import Entity
from game.enemies.enemy_registry import register_enemy
from game.menu.menu_state import MenuState

class EMPRadar(Entity):
    def __init__(self, x, y, level):
        super().__init__(x, y, "assets/characters/drone.png", "assets/characters/drone.json", level, None)
        self.max_health = 30
        self.health = self.max_health
        self.level = level

    def update(self, level, dt):
        super().update(level, dt)

    def eliminate(self):
        super().eliminate()
        self.level.player.abilities_blocked = False


@register_enemy("neuros")
class Neuros(Entity):
    def __init__(self, x, y, sprite_path, json_path, player, level, sound_manager):
        super().__init__(x, y, sprite_path, json_path, level, sound_manager)
        self.player = player
        self.level = level

        self.phase_configs = {
            1: {"health": 10, "speed": 40},
            2: {"health": 12, "speed": 60},
            3: {"health": 16, "speed": 80}
        }

        self.phase = 1
        self.set_phase_stats(1)
        self.ai_state = "sabotage"
        self.shielded = False
        self.hits_taken = 0
        self.speed = 0
        self.drones = []
        self.emp_radars = []
        self.timer = 0
        self.action_cooldown = 0
        self.text_timer = 0
        self.text_duration = 3.0
        self.current_text = ""
        self.detection_range = 500
        self.death_executed = False

    def set_phase_stats(self, phase):
        config = self.phase_configs[phase]
        self.max_health = config["health"]
        self.health = self.max_health
        self.speed = config["speed"]

    def update(self, level, dt):
        super().update(level, dt)

        self.update_text(dt)
        self.action_cooldown -= dt

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

    def speak(self, text, duration=3.0):
        self.current_text = text
        self.text_timer = duration

    # === Phase 1 ===
    def phase_1(self, dt):
        self.set_state("analyze")
        target_pos = pygame.Vector2(self.player.rect.center) + pygame.Vector2(0, 50 if self.is_flipped else -50)
        direction = target_pos - self.rect.center
        if direction.length() > 10:
            direction.normalize_ip()
            self.velocity = direction * self.speed * dt
        else:
            self.velocity.update(0, 0)

        if self.action_cooldown <= 0:
            self.speak("Analyzing human behavior...")
            self.action_cooldown = 3.0

        if self.health < self.max_health * 0.8:
            self.enter_next_phase()

    # === Phase 2 ===
    def phase_2(self, dt):
        self.set_state("attack")

        if self.action_cooldown <= 0:
            attack = random.choice([self.summon_drones, self.deploy_emp_radars])
            attack()
            self.action_cooldown = random.uniform(2.0, 4.0)

        self.move_towards_player(dt)

        if self.health < self.max_health * 0.6 and not self.emp_radars:
            self.enter_next_phase()

    # === Phase 3 ===
    def phase_3(self, dt):
        if self.shielded:
            self.timer -= dt
            if self.timer <= 0:
                self.shielded = False
                self.ai_state = "attack"
                self.speak("Shield depleted.")

        self.set_state("attack")

        if self.action_cooldown <= 0:
            attack = random.choice([
                self.summon_drones,
                self.deploy_emp_radars,
                self.shoot_lasers,
                self.shield_self,
                self.summon_heal_drones,
                self.world_hack,
                self.fast_dash,
                self.slow_time
            ])
            attack()
            self.action_cooldown = random.uniform(1.0, 3.0)

        self.move_towards_player(dt)

    def move_towards_player(self, dt):
        direction = pygame.Vector2(self.player.rect.center) - self.rect.center
        if direction.length() > 50:
            direction.normalize_ip()
            self.velocity.x = direction.x * self.speed * dt

    def enter_next_phase(self):
        self.phase += 1
        if self.phase > 3:
            return
        self.set_phase_stats(self.phase)
        self.stun = 20
        self.ai_state = "attack" if self.phase == 3 else "counter"
        self.hits_taken = 0

        if self.phase == 2:
            self.speak("Analysis complete. Initiating countermeasures.")
        elif self.phase == 3:
            self.speak("You are an annoyance. Termination protocol engaged.")

    # Attacks
    def summon_heal_drones(self):
        pass

    def summon_drones(self):
        if len(self.drones) < 5:
            pos = (self.rect.centerx + random.randint(-40, 40), self.rect.y)
            drone = Drone(pos[0], pos[1], "assets/characters/drone.png", "assets/characters/drone.json",
                          self.player, self.level, self.sound_manager)
            self.drones.append(drone)
            self.level.enemies.add(drone)
            self.speak("Deploying additional units.")

    def deploy_emp_radars(self):
        if len(self.emp_radars) < 3:
            pos = (self.rect.centerx + random.randint(-100, 100), self.rect.top - 40)
            radar = EMPRadar(pos[0], pos[1], self.level)
            self.emp_radars.append(radar)
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
        self.velocity = direction * self.speed * 2

    def slow_time(self):
        self.level.engine.fps = 30  # Should reset externally
        self.speak("Temporal manipulation active.")
        self.timer = 3.0

    def hit(self, attacker, stun=20):
        if self.shielded:
            return
        super().hit(attacker, stun)
        self.hits_taken += 1
        if self.phase == 3 and self.hits_taken >= 3:
            self.shield_self()

    def eliminate(self):
        if self.phase == 3 and not self.death_executed:
            self.death_executed = True
            for drone in self.drones:
                drone.eliminate()
            for radar in self.emp_radars:
                radar.eliminate()
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
