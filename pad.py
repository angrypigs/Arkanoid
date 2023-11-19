from pygame import Rect

class Pad:

    def __init__(self, surf, width: int, height: int, color: tuple, flat: int, image) -> None:
        self.surf = surf
        self.HEIGHT = height
        self.width = width
        self.COLOR = color
        self.FLAT = flat
        self.image = image
    
    def draw(self, x: float) -> None:
        self.pad = Rect(x-self.width//2, self.FLAT, self.width, self.HEIGHT)
        self.surf.blit(self.image, (x-self.width//2, self.FLAT))
