import pygame
import os
import sys
from cryptography.fernet import Fernet
from math import atan, pi
from ball import Ball
from pad import Pad
from brick import Brick


class Game:

    def __init__(self) -> None:
        # init constants and variables
        self.WIDTH = 1000
        self.HEIGHT = 700
        self.KEY = b'1fM3z8hZKFlNgF5UAKpIjEkeU3SDxPenJP725BN-V9Q='
        self.fernet = Fernet(self.KEY)
        self.run = True
        self.balls : list[Ball] = []
        self.bricks : list[list[Brick|None]] = [[None for x in range(14)] for y in range(10)]
        # init pygame window
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Arkanoid")
        self.clock = pygame.time.Clock()
        self.init_images()
        # add ball, pad and bricks
        self.balls.append(Ball(self.screen, (130, 130, 170), 8, 100, 500, 80))
        self.pad = Pad(self.screen, 150, 20, (150, 150, 110), self.HEIGHT/9*8)
        self.load_level(1)
        # game loop
        while self.run:
            self.screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
            self.mouse_x, mouse_y = pygame.mouse.get_pos()
            self.pad.draw(pygame.math.clamp(self.mouse_x, 75, self.WIDTH-75))
            self.draw_balls_and_bricks()
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
        brick_list = [[(1 if i%2==0 else 6) for i in range(14)], 
                      [9 for i in range(14)],
                      [10 for i in range(14)],
                      [11 for i in range(14)],
                      [12 for i in range(14)],
                      [0 for i in range(14)],
                      [(0 if i%2==0 else 6) for i in range(14)]]
        for i in range(3):
            brick_list.append([0 for i in range(14)])
        # with open(self.res_path(f"levels\\level{level}.dat"), "rb") as f:
        #     for line in f.readlines():
        #         brick_list = [x.split(":") for x in self.fernet.decrypt(self.KEY).decode().split(";")]
        # for i in brick_list:
        #     print(i)
        for i in range(10):
            for j in range(14):
                if brick_list[i][j]:
                    self.bricks[i][j] = Brick(self.screen, 52+j*64, 52+i*32, brick_list[i][j], self.images["bricks"][brick_list[i][j]])

    def draw_balls_and_bricks(self) -> None:
        # draw all balls and bricks from lists
        for ball in self.balls:
            ball.draw(1)
        for row in range(10):
            for col in range(14):
                if self.bricks[row][col]!=None: self.bricks[row][col].draw()

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
            if ball.radius>=ball.coords[0] or ball.coords[0]>=self.WIDTH-ball.radius:
                ball.power[0] *= -1
                ball.coords += ball.power*2
            if ball.radius>=ball.coords[1] or ball.coords[1]>=self.HEIGHT-ball.radius:
                ball.power[1] *= -1
                ball.coords += ball.power*2
            # bricks collision
            for row in range(10):
                for col in range(14):
                    brick = self.bricks[row][col]
                    if brick != None and ball.ball.colliderect(brick.brick):
                        flag = False
                        if abs(ball.ball.bottom-brick.brick.top)<5 and ball.power[1]>0:
                            ball.power[1] *= -1
                            flag = True
                        elif abs(ball.ball.top-brick.brick.bottom)<5 and ball.power[1]<0:
                            ball.power[1] *= -1
                            flag = True
                        if abs(ball.ball.right-brick.brick.left)<5 and ball.power[0]>0:
                            ball.power[0] *= -1
                            flag = True
                        elif abs(ball.ball.left-brick.brick.right)<5 and ball.power[0]<0:
                            ball.power[0] *= -1
                            flag = True
                        if flag:
                            if brick.index in [1, 2, 3, 4, 5, 12]:
                                self.bricks[row][col] = None
                            elif brick.index in [9, 10, 11]:
                                brick.index += 1
                                brick.image = self.images["bricks"][brick.index]
                            ball.coords += ball.power
                            break
    
    def init_images(self) -> None:
        """Import game images to dict"""
        self.images = {"bricks": []}
        for img in os.listdir(self.res_path("assets\\bricks")):
            self.images["bricks"].append(img)
        self.images["bricks"] = sorted(self.images["bricks"], key=lambda x: int(x.lstrip("brick").rstrip(".png")))
        self.images["bricks"].insert(0, None)
        for i, img in enumerate(self.images["bricks"]):
            if img!=None:
                self.images["bricks"][i] = pygame.image.load(self.res_path(f"assets\\bricks\\{img}"))



if __name__ == "__main__":
    Game()
        