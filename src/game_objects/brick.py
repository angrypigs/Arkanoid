from pygame import Rect

class Brick:

    def __init__(self, surf, x: int, y: int, index: int, image) -> None:
        self.surf = surf
        self.X = x
        self.Y = y
        self.image = image
        self.index = index

    def draw(self) -> None:
        self.mask = Rect(self.X, self.Y, 64, 32)
        self.surf.blit(self.image, (self.X, self.Y))