from pygame.draw import circle
from pygame.math import Vector2
from pygame import Rect

class Ball:

    def __init__(self, surf, color: tuple, radius: float, x: int, y: int, angle: int) -> None:
        self.coords = Vector2(x, y)
        self.speed = 3
        self.power = Vector2(self.speed, 0).rotate(angle)
        self.COLOR = color
        self.radius = radius
        self.rect_rad = radius+5
        self.surf = surf
        
    
    def draw(self, move: bool) -> None:
        self.ball = Rect(self.coords - (self.rect_rad, self.rect_rad), (self.rect_rad*2, self.rect_rad*2))
        circle(self.surf, self.COLOR, self.coords, self.radius)
        if move: self.coords += self.power
        
