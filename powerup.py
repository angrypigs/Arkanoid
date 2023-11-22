from pygame import Rect



class PowerUp:

    def __init__(self, screen, x: int, y: int, height: int, powerup_type: str, image) -> None:
        self.screen = screen
        self.HEIGHT = height
        self.x = x-17
        self.y = y
        self.type = powerup_type
        self.image = image

    def __bool__(self) -> bool:
        return self.y<self.HEIGHT

    def draw(self, move: bool) -> None:
        self.mask = Rect(self.x, self.y, 35, 35)
        self.screen.blit(self.image, (self.x, self.y))
        if move: self.y += 2