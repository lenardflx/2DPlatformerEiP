class Ability:
    def __init__(self, level, player, cooldown):
        self.player = player
        self.cooldown = cooldown
        self.current_cooldown = 0
        self.level = level
        self.sound_manager = level.sound_manager

    def activate(self):
        self.current_cooldown = self.cooldown

    def can_activate(self):
        return self.current_cooldown <= 0

    def update(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

class DoubleJumpAbility(Ability):
    def __init__(self, level,player):
        super().__init__(level, player, cooldown=150)
        self.used = False

    def reset(self):
        self.used = False

class GravityInverseAbility(Ability):
    def __init__(self, level, player):
        super().__init__(level, player, cooldown=150)

    def activate(self):
        if not self.can_activate():
            return False
        self.sound_manager.play_sfx("gravity_inverse")
        self.level.flip_gravity()
        self.current_cooldown = self.cooldown
        return True
