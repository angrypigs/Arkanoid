from pygame.draw import circle
from pygame.math import Vector2

class Ball:

    def __init__(self, surf, color: tuple, radius: float, x: int, y: int, angle: int) -> None:
        self.coords = Vector2(x, y)
        self.power = Vector2(3, 0).rotate(angle)
        self.COLOR = color
        self.radius = radius
        self.surf = surf
        self.speed = 3
    
    def draw(self, move: bool) -> None:
        self.ball = circle(self.surf, self.COLOR, self.coords, self.radius)
        if move: self.coords += self.power
        
