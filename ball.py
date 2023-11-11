from pygame.draw import circle
from pygame.math import Vector2
from pygame import Rect

class Ball:

    def __init__(self, surf, radius: float, x: int, y: int, angle: int, image) -> None:
        self.coords = Vector2(x, y)
        self.speed = 4
        self.power = Vector2(self.speed, 0).rotate(angle)
        self.radius = radius
        self.rect_rad = radius+5
        self.image = image
        self.surf = surf
        
    
    def draw(self, move: bool) -> None:
        self.ball = Rect(self.coords-(self.radius, self.radius), (self.radius*2, self.radius*2))
        self.surf.blit(self.image, self.coords-(self.radius, self.radius))
        if move: self.coords += self.power
        
