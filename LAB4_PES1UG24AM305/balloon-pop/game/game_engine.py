"""
GameEngine: owns all balloons, spawns new ones, and handles clicks.

Three balloon types (normal / bonus / penalty) spawned with weights.
Lives system: a balloon falling past the bottom costs 1 life; at 0 lives
the game ends. No timer yet.
"""

import random

from game.balloon import Balloon
from game.click_detection import check_pop
from game.renderer import WIDTH, HEIGHT

SPAWN_INTERVAL_FRAMES = 45
STARTING_LIVES = 3

# Spawn weights per balloon type (roughly 70% / 15% / 15%).
SPAWN_WEIGHTS = {
    "normal": 70,
    "bonus": 15,
    "penalty": 15,
}


class GameEngine:
    def __init__(self):
        self.balloons = []
        self.frames_until_spawn = 0
        self.score = 0
        self.lives = STARTING_LIVES

    @property
    def game_over(self):
        return self.lives <= 0

    def _spawn_balloon(self):
        radius = random.randint(16, 44)
        x = random.randint(radius + 10, WIDTH - radius - 10)
        speed = random.uniform(1.5, 3.0)
        balloon_type = random.choices(
            list(SPAWN_WEIGHTS.keys()),
            weights=list(SPAWN_WEIGHTS.values()),
        )[0]
        self.balloons.append(
            Balloon(x=x, y=-radius, radius=radius, speed=speed, balloon_type=balloon_type)
        )

    def handle_click(self, pos):
        if self.game_over:
            return
        popped = check_pop(self.balloons, pos)
        if popped is not None:
            # Popping only changes score, never lives (even for penalty balloons).
            self.balloons.remove(popped)
            self.score += popped.points

    def update(self):
        if self.game_over:
            return  # freeze: no spawning, no movement

        self.frames_until_spawn -= 1
        if self.frames_until_spawn <= 0:
            self._spawn_balloon()
            self.frames_until_spawn = SPAWN_INTERVAL_FRAMES

        for b in self.balloons:
            b.update()

        remaining = []
        for b in self.balloons:
            if b.is_past_bottom(HEIGHT):
                self.lives -= 1
            else:
                remaining.append(b)
        self.balloons = remaining

        # Several balloons can escape in the same frame; don't go below 0.
        self.lives = max(self.lives, 0)

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.balloons)
        renderer.draw_text(surface, font, f"Score: {self.score}   Lives: {self.lives}", (10, 10))
        if self.game_over:
            renderer.draw_banner(surface, font, f"Game Over - Final Score: {self.score}")