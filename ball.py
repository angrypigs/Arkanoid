from pygame.draw import circle
from pygame.math import Vector2
from math import sin, cos, radians

class Ball:

    def __init__(self, surf, color: tuple, radius: float, x: int, y: int, angle: int) -> None:
        self.coords = Vector2(x, y)
        self.power = Vector2(3, 0).rotate(angle)
        self.COLOR = color
        self.radius = radius
        self.surf = surf
        self.speed = 5
    
    def draw(self, speed: float) -> None:
        self.ball = circle(self.surf, self.COLOR, self.coords, self.radius)
        self.power *= speed
        self.coords += self.power
        
