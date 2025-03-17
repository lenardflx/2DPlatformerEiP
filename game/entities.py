class entity:
    #   x position x
    #   y position y
    #   speed is walking speed
    #   max_health is max health
    def __init__(self, x, y, speed, max_health):
        self.speed = speed
        self.max_health = max_health
        self.health = max_health
        self.x = x
        self.y = y

    def move_left(self):
        self.x = self.x - self.speed

    def move_right(self):
        self.x = self.x + self.speed

