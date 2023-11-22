from pygame import Rect



class Bullet:

    def __init__(self, screen, x: int, y: int, cols: int, image) -> None:
        self.screen = screen
        self.X = x
        self.y = y
        self.COL = max(min(int(self.X-20)//64, cols-1), 0)
        self.image = image

    def __bool__(self) -> bool:
        return self.y>=50

    def draw(self, move: bool) -> None:
        self.mask = Rect(self.X, self.y, 3, 14)
        self.screen.blit(self.image, (self.X, self.y))
        if move: self.y -= 4