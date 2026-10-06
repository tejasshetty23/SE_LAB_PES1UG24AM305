"""
Balloon: falls from the top of the screen. The player must pop it
before it reaches the bottom. Balloons vary in size - this matters for
how click detection should work.
"""

import pygame

# Each balloon type defines its color and the score change when popped.
BALLOON_TYPES = {
    "normal":  {"color": (220, 40, 40),  "points": 10},   # red
    "bonus":   {"color": (230, 190, 40), "points": 30},   # gold
    "penalty": {"color": (90, 30, 110),  "points": -20},  # dark purple
}


class Balloon:
    def __init__(self, x, y, radius, speed, balloon_type="normal"):
        if balloon_type not in BALLOON_TYPES:
            raise ValueError(f"Unknown balloon type: {balloon_type}")
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.balloon_type = balloon_type
        self.color = BALLOON_TYPES[balloon_type]["color"]
        self.points = BALLOON_TYPES[balloon_type]["points"]

    def update(self):
        self.y += self.speed

    def is_past_bottom(self, height):
        return self.y - self.radius > height

    def get_rect(self):
        return pygame.Rect(
            int(self.x - self.radius), int(self.y - self.radius),
            self.radius * 2, self.radius * 2,
        )