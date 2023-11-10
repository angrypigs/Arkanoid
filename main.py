import pygame
import os
import sys
from cryptography.fernet import Fernet
from math import atan, pi, sqrt
from random import choice
from ball import Ball
from pad import Pad
from brick import Brick


class Game:

    def __init__(self) -> None:
        # init constants and variables
        self.WIDTH = 1000
        self.HEIGHT = 700
        self.ROWS = 10
        self.COLS = 15
        self.KEY = b'1fM3z8hZKFlNgF5UAKpIjEkeU3SDxPenJP725BN-V9Q='
        self.fernet = Fernet(self.KEY)
        self.run = True
        self.pause = True
        self.balls : list[Ball] = []
        self.bricks : list[list[Brick|None]] = [[None for x in range(self.COLS)] for y in range(self.ROWS)]
        # init pygame window
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Arkanoid")
        self.clock = pygame.time.Clock()
        self.init_images()
        # add ball, pad and bricks
        self.balls.append(Ball(self.screen, (130, 130, 170), 10, self.WIDTH//2, 600, -60))
        self.pad = Pad(self.screen, 150, 20, (150, 150, 110), self.HEIGHT/9*8)
        self.pad_x = self.WIDTH//2
        self.load_level(9)
        # main loop
        while self.run:
            self.screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.pause = not self.pause
            self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
            if not self.pause: self.pad_x = self.mouse_x
            self.pad.draw(pygame.math.clamp(self.pad_x, 95, self.WIDTH-95))
            self.draw_game()
            self.balls_collisions()
            pygame.display.flip()
            self.clock.tick(120)
        
    def res_path(self, rel_path: str) -> str:
        """
        Return path to file modified by auto_py_to_exe path if packed to exe already
        """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = sys.path[0]
        return os.path.join(base_path, rel_path)

    def load_level(self, level: int) -> None:
        with open(self.res_path(os.path.join("levels", f"level{level}.dat")), "rb") as f:
            for line in f.readlines():
                brick_list = [[int(y) for y in x.split(":")] for x in self.fernet.decrypt(line).decode().split(";")]
        for i in brick_list:
            print(i)
        for i in range(self.ROWS):
            for j in range(self.COLS):
                if brick_list[i][j]:
                    self.bricks[i][j] = Brick(self.screen, 20+j*64, 50+i*32, brick_list[i][j], self.images["bricks"][brick_list[i][j]])

    def draw_game(self) -> None:
        # draw game components
        self.screen.blit(self.images["game_gui"], (0, 0))
        for ball in self.balls:
            ball.draw(not self.pause)
        for row in range(self.ROWS):
            for col in range(self.COLS):
                if self.bricks[row][col]!=None: 
                    self.bricks[row][col].draw()

    def balls_collisions(self) -> None:
        """ check for collision of every ball with walls, pad and all bricks """
        for ball in self.balls:
            # pad collision
            if ball.ball.colliderect(self.pad.pad):
                offset = (ball.coords[0]-self.mouse_x)/self.pad.WIDTH
                angle = atan(ball.power[1]/ball.power[0])
                angle2 = (pi/2-abs(angle))*(1 if angle<0 else -1)/pi
                ball.power[1] *= -1
                ball.power.rotate_ip(180*min(max(offset+angle2, -0.5), 0.5))
                ball.coords += ball.power*3
                ball.coords[1] -= 5
            # walls collision
            if ball.radius+30>=ball.coords[0] or ball.coords[0]>=self.WIDTH-ball.radius-30:
                ball.power[0] *= -1
                ball.coords += ball.power*2
            if ball.radius+60>=ball.coords[1] or ball.coords[1]>=self.HEIGHT-ball.radius:
                ball.power[1] *= -1
                ball.coords += ball.power*2
            # bricks collision
            b, a = int(ball.coords[0]-20)//64, int(ball.coords[1]-50)//32
            cells = [[x, y] for x in range(a-1, a+2) for y in range(b-2, b+3) if
                     0<=x<self.ROWS and 0<=y<self.COLS and self.bricks[x][y] is not None]
            for row, col in cells:
                brick = self.bricks[row][col]
                circle_closest_x = max(brick.X, min(ball.coords[0], brick.X + 64))
                circle_closest_y = max(brick.Y, min(ball.coords[1], brick.Y + 32))
                dist = sqrt((ball.coords[0] - circle_closest_x) ** 2 + (ball.coords[1] - circle_closest_y) ** 2)
                if dist < ball.radius:
                    overlap_x = circle_closest_x - ball.coords[0]
                    overlap_y = circle_closest_y - ball.coords[1]
                    if abs(overlap_x) < abs(overlap_y):
                        if overlap_y > 0 and ball.power[1]>0:
                            ball.ball.bottom = brick.brick.top
                            ball.power[1] *= -1
                        elif overlap_y < 0 and ball.power[1]<0:
                            ball.ball.top = brick.brick.bottom
                            ball.power[1] *= -1
                    else:
                        if overlap_x > 0 and ball.power[0]>0:
                            ball.ball.right = brick.brick.left
                            ball.power[0] *= -1
                        elif overlap_x < 0 and ball.power[0]<0:
                            ball.ball.left = brick.brick.right
                            ball.power[0] *= -1
                    if brick.index in [1, 2, 3, 4, 5, 12]:
                        self.bricks[row][col] = None
                    elif brick.index in [9, 10, 11]:
                        brick.index += 1
                        brick.image = self.images["bricks"][brick.index]
                    elif brick.index == 8:
                        brick.index = choice([1, 2, 3, 4, 5, 7, 9, 10, 11, 12])
                        brick.image = self.images["bricks"][brick.index]
                    elif brick.index == 7:
                        self.bricks[row][col] = None
                        for i in [x for x in [[row, col-1], [row, col+1], [row-1, col], [row+1, col]]
                                    if 0<=x[0]<self.ROWS and 0<=x[1]<self.COLS and self.bricks[x[0]][x[1]]!=None]:
                            self.bricks[i[0]][i[1]] = None
    
    def init_images(self) -> None:
        """Import game images to dict"""
        self.images = {"bricks": []}
        self.images["game_gui"] = pygame.image.load(self.res_path(os.path.join("assets/gui", "game_gui.png")))
        for img in os.listdir(self.res_path(f"assets{os.path.sep}bricks")):
            self.images["bricks"].append(img)
        self.images["bricks"] = sorted(self.images["bricks"], key=lambda x: int(x.lstrip("brick").rstrip(".png")))
        self.images["bricks"].insert(0, None)
        for i, img in enumerate(self.images["bricks"]):
            if img!=None:
                self.images["bricks"][i] = pygame.image.load(self.res_path(os.path.join("assets/bricks", img)))
                



if __name__ == "__main__":
    Game()
        