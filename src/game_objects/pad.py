from pygame import Rect

class Pad:

    def __init__(self, surf, width: int, height: int, flat: int, image) -> None:
        self.surf = surf
        self.HEIGHT = height
        self.width = width
        self.FLAT = flat
        self.image = image
        self.x = 100
    
    def draw(self, x: float) -> None:
        self.mask = Rect(x-self.width//2, self.FLAT, self.width, self.HEIGHT)
        self.surf.blit(self.image, (x-self.width//2, self.FLAT))
        self.x = x
