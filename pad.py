from pygame.draw import rect

class Pad:

    def __init__(self, surf, width: int, height: int, color: tuple, flat: int) -> None:
        self.surf = surf
        self.HEIGHT = height
        self.WIDTH = width
        self.COLOR = color
        self.FLAT = flat
    
    def draw(self, x: float) -> None:
        self.pad = rect(self.surf, self.COLOR, (x-self.WIDTH//2, self.FLAT, self.WIDTH, self.HEIGHT))
