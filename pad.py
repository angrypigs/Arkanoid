from pygame import Rect

class Pad:

    def __init__(self, surf, width: int, height: int, color: tuple, flat: int, image) -> None:
        self.surf = surf
        self.HEIGHT = height
        self.WIDTH = width
        self.COLOR = color
        self.FLAT = flat
        self.image = image
    
    def draw(self, x: float) -> None:
        self.pad = Rect(x-self.WIDTH//2, self.FLAT, self.WIDTH, self.HEIGHT)
        self.surf.blit(self.image, (x-self.WIDTH//2, self.FLAT))
