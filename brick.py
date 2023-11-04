from pygame.draw import rect

class Brick:

    def __init__(self, surf, x: int, y: int, color: tuple) -> None:
        self.surf = surf
        self.X = x
        self.Y = y
        self.COLOR = color

    def draw(self) -> None:
        self.brick = rect(self.surf, self.COLOR, (self.X, self.Y, 64, 32), width=2)