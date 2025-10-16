import numpy as np
import random

EMPTY_WEIGHT = 8
MAX_TAKEOFF_WEIGHT = 15
MAX_PAYLOAD = 2.5
ENDURANCE = 90 * 60
MAX_SPEED = 10
OPERATIONAL_ALTITUDE = (60, 120)
FIRING_RANGE = (30, 250)

NUM_FRIENDLY = 3
NUM_ENEMY = 4
ARENA_SIZE = 500
DETECTION_RANGE = 80
TIME_STEP = 1

class Drone:
    def __init__(self, drone_id, x, y, is_enemy=False):
        self.id = drone_id
        self.x = x
        self.y = y
        self.altitude = random.randint(*OPERATIONAL_ALTITUDE)
        self.is_enemy = is_enemy
        self.color = "red" if is_enemy else "lime"
        self.alive = True
        self.energy = ENDURANCE
        self.explosion_timer = 0

    def move(self, target=None):
        if not self.alive or self.energy <= 0:
            return
        if self.is_enemy:
            dx, dy = np.random.uniform(-1, 1), np.random.uniform(-1, -0.3)
        else:
            if target is not None:
                dx, dy = target.x - self.x, target.y - self.y
            else:
                dx, dy = np.random.uniform(-1, 1), np.random.uniform(-1, 1)
        norm = np.sqrt(dx**2 + dy**2)
        if norm > 0:
            dx, dy = (dx / norm) * MAX_SPEED, (dy / norm) * MAX_SPEED
        self.x = np.clip(self.x + dx, 0, ARENA_SIZE)
        self.y = np.clip(self.y + dy, 0, ARENA_SIZE)
        self.energy -= TIME_STEP

friendly_drones = [Drone(i, random.randint(100, 400), random.randint(150, 250))
                   for i in range(NUM_FRIENDLY)]
enemy_drones = [Drone(i, random.randint(150, 400), random.randint(300, 450), is_enemy=True)
                for i in range(NUM_ENEMY)]
