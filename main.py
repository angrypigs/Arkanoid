import pygame
import os
import sys
from math import atan, pi
from ball import Ball
from pad import Pad
from brick import Brick


class Game:

    def __init__(self) -> None:
        self.WIDTH = 1000
        self.HEIGHT = 700
        self.run = True
        self.balls : list[Ball] = []
        self.bricks : list[list[Brick|None]] = [[None for x in range(14)] for y in range(10)]
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Arkanoid")
        self.clock = pygame.time.Clock()
        self.balls.append(Ball(self.screen, (130, 130, 170), 8, 100, 500, 80))
        self.pad = Pad(self.screen, 150, 20, (150, 150, 110), self.HEIGHT/9*8)
        self.init_images()
        for i in range(10):
            for j in range(14):
                self.bricks[i][j] = Brick(self.screen, 52+j*64, 52+i*32, (150, 150, 90))
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
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = sys.path[0]
        return os.path.join(base_path, rel_path)

    def draw_balls_and_bricks(self) -> None:
        for ball in self.balls:
            ball.draw(1)
        for row in range(10):
            for col in range(14):
                if self.bricks[row][col]!=None: self.bricks[row][col].draw()

    def balls_collisions(self) -> None:
        for ball in self.balls:
            if ball.ball.colliderect(self.pad.pad):
                offset = (ball.coords[0]-self.mouse_x)/self.pad.WIDTH
                angle = atan(ball.power[1]/ball.power[0])
                angle2 = (pi/2-abs(angle))*(1 if angle<0 else -1)/pi
                ball.power[1] *= -1
                ball.power.rotate_ip(180*min(max(offset+angle2, -0.5), 0.5))
                ball.coords += ball.power*3
                ball.coords[1] -= 5
            if ball.radius>=ball.coords[0] or ball.coords[0]>=self.WIDTH-ball.radius:
                ball.power[0] *= -1
                ball.coords += ball.power*2
            if ball.radius>=ball.coords[1] or ball.coords[1]>=self.HEIGHT-ball.radius:
                ball.power[1] *= -1
                ball.coords += ball.power*2
            for row in range(10):
                for col in range(14):
                    brick = self.bricks[row][col]
                    if brick != None and ball.ball.colliderect(brick.brick):
                        if abs(ball.ball.bottom-brick.brick.top)<5 and ball.power[1]>0:
                            ball.power[1] *= -1
                            self.bricks[row][col] = None
                            ball.coords += ball.power
                            break
                        elif abs(ball.ball.top-brick.brick.bottom)<5 and ball.power[1]<0:
                            ball.power[1] *= -1
                            self.bricks[row][col] = None
                            ball.coords += ball.power
                            break
                        elif abs(ball.ball.right-brick.brick.left)<5 and ball.power[0]>0:
                            ball.power[0] *= -1
                            self.bricks[row][col] = None
                            ball.coords += ball.power
                            break
                        elif abs(ball.ball.left-brick.brick.right)<5 and ball.power[0]<0:
                            ball.power[0] *= -1
                            self.bricks[row][col] = None
                            ball.coords += ball.power
                            break
    
    def init_images(self) -> None:
        self.images = {"bricks": []}
        for img in os.listdir(self.res_path("assets\\bricks")):
            self.images["bricks"].append(img)
        self.images["bricks"] = sorted(self.images["bricks"], key=lambda x: int(x.lstrip("brick").rstrip(".png")))
        print(self.images["bricks"])



if __name__ == "__main__":
    Game()
        