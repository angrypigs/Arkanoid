import pygame
import os
import sys
from time import sleep
from threading import Thread
from cryptography.fernet import Fernet
from math import atan, pi, sqrt
from random import choice, sample, randint

from ball import Ball
from pad import Pad
from brick import Brick
from powerup import PowerUp
from custom_timer import customTimer
from utils import *


class Game:

    def __init__(self) -> None:
        # init constants and variables
        self.WIDTH = 1000
        self.HEIGHT = 700
        self.ROWS = 10
        self.COLS = 15
        self.KEY = b'1fM3z8hZKFlNgF5UAKpIjEkeU3SDxPenJP725BN-V9Q='
        self.LEVELS_AMOUNT = len([img for img in os.listdir(res_path("levels")) 
                                  if img.startswith("level")])
        self.fernet = Fernet(self.KEY)
        self.run = True
        self.pause = False
        self.game_mode = 2
        self.current_level = 0
        self.balls : list[Ball] = []
        self.bricks : list[list[Brick|None]] = [[None for x in range(self.COLS)] 
                                                for y in range(self.ROWS)]
        
        self.powerups_places : list[list[int]] = []
        self.powerups : list[PowerUp] = []
        # 0 - pad length, 1 - ball speed, 2 - border, 3 - shooting pad, 4 - glue, 5 - blindness, 6 - multiplier
        self.powerup_threads : list[customTimer] = [customTimer(20, self.reset_powerup, [x, ]) for x in range(7)]
        self.POWERUP_DEFAULTS = [120, 4, False, False, False, False, 1]
        self.powerup_values : list[int|bool] = self.POWERUP_DEFAULTS.copy()
        # init pygame window
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Arkanoid")
        self.clock = pygame.time.Clock()
        self.init_images()
        # add ball and pad
        self.pad = Pad(self.screen, 120, 20, (150, 150, 110), self.HEIGHT/9*8, self.images["pads"]["0"]["normal"])
        self.pad_x = self.WIDTH//2
        # main loop
        while self.run:
            self.screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                elif event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
                    self.pause = not self.pause
            if self.game_mode==2:
                self.game_mode = 0
                if self.current_level==self.LEVELS_AMOUNT:
                    self.current_level = 1
                else:
                    self.current_level += 1
                self.change_game_mode(3, 1)
                self.pad_x = self.WIDTH//2
                self.load_level(self.current_level)
            self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
            if not self.pause and self.game_mode==1: self.pad_x = self.mouse_x
            self.pad.draw(pygame.math.clamp(self.pad_x, 20+self.powerup_values[0]//2, self.WIDTH-20-self.powerup_values[0]//2))
            self.draw_game()
            self.balls_collisions()
            pygame.display.flip()
            self.clock.tick(120)

    def change_game_mode(self, time: float, mode: int) -> None:
        def change() -> None:
            sleep(time)
            self.game_mode = mode
        Thread(target=change, daemon=True).start()

    def reset_powerup(self, index: int) -> None:
        self.powerup_values[index] = self.POWERUP_DEFAULTS[index]
        match index:
            case 0:
                self.pad.image = self.images["pads"]["0"]["shooting" if self.powerup_values[3] else "normal"]
                self.pad.width = 120
            case 1:
                for ball in self.balls:
                    ball.power *= (self.powerup_values[1]/ball.speed)
                    ball.speed = self.powerup_values[1]
            case 5:
                match self.powerup_values[0]:
                    case 90:
                        length = "2"
                    case 160:
                        length = "1"
                    case _:
                        length = "0"
                self.pad.image = self.images["pads"][length]["normal"]
            case 6:
                self.balls.sort(key=lambda y: y.coords[1])
                while len(self.balls)!=1:
                    self.balls.pop()

    def load_level(self, level: int) -> None:
        
        with open(res_path(os.path.join("levels", f"level{level}.dat")), "rb") as f:
            for line in f.readlines():
                brick_list = [[int(y) for y in x.split(":")] 
                              for x in self.fernet.decrypt(line).decode().split(";")]
        powerups = []
        self.powerups.clear()
        self.powerups_places.clear()
        for i in range(self.ROWS):
            for j in range(self.COLS):
                self.bricks[i][j] = None
                if brick_list[i][j]:
                    powerups.append([i, j])
                    self.bricks[i][j] = Brick(self.screen, 20+j*64, 50+i*32, 
                                              brick_list[i][j], self.images["bricks"][brick_list[i][j]])
        self.powerups_places.extend(sample(powerups, 10))
        self.balls.clear()
        self.balls.append(Ball(self.screen, 10, self.WIDTH//2, 600, -60, self.images["balls"]["normal"]))

    def draw_game(self) -> None:
        """
        Draw game components
        """
        self.screen.blit(self.images["game_gui"], (0, 0))
        for ball in self.balls:
            ball.draw(not self.pause and self.game_mode==1)
        for row in range(self.ROWS):
            for col in range(self.COLS):
                if self.bricks[row][col]!=None and not self.powerup_values[5]:
                    self.bricks[row][col].draw()
        for powerup in self.powerups:
            powerup.draw(not self.pause and self.game_mode==1)

    def balls_collisions(self) -> None:
        """ 
        Check for collision of every ball with walls, pad and all bricks, 
        and pad with every powerup
        """
        # powerups collision
        for i, power_up in enumerate(self.powerups):
            if not power_up:
                self.powerups.pop(i)
            elif power_up.powerup.colliderect(self.pad.pad):
                index = powerup_index(power_up.type)
                new_val = powerup_value(power_up.type, self.powerup_values[6])
                self.powerup_values[index] = new_val
                match index:
                    case 0:
                        self.pad.image = self.images["pads"]["1" if new_val==160 else "2"]["shooting" if self.powerup_values[3] else "normal"]
                        self.pad.width = self.powerup_values[0]
                    case 1:
                        for ball in self.balls:
                            ball.power *= (new_val/ball.speed)
                            ball.speed = new_val
                    case 6:
                        self.balls.sort(key=lambda y: y.coords[1])
                        for j in range(2):
                            coords = self.balls[0].coords
                            self.balls.append(Ball(self.screen, 10, coords[0], coords[1], randint(-80, -40), self.images["balls"]["normal"]))

                self.powerup_threads[index].reset()
                self.powerups.pop(i)
        for ball in self.balls:
            # pad collision
            if ball.ball.colliderect(self.pad.pad) and ball.power[1]>=0:
                offset = (ball.coords[0]-self.mouse_x)/self.pad.width
                angle = atan(ball.power[1]/ball.power[0])
                angle2 = (pi/2-abs(angle))*(1 if angle<0 else -1)/pi
                ball.power[1] *= -1
                ball.power.rotate_ip(180*min(max(offset+angle2, -0.5), 0.5))
                if ball.power[1]>0: ball.power[1] *= -1
                ball.coords += ball.power*3
                ball.coords[1] -= 5
            # walls collision
            if ball.radius+20>=ball.coords[0]:
                ball.power[0] *= -1
                ball.ball.left = 25
            elif ball.coords[0]>=self.WIDTH-ball.radius-20:
                ball.power[0] *= -1
                ball.ball.right = self.WIDTH-25
            if ball.radius+50>=ball.coords[1]:
                ball.power[1] *= -1
                ball.ball.top = 55
            elif ball.coords[1]>=self.HEIGHT-ball.radius:
                if len(self.balls)==1:
                    self.game_mode = 0
                    self.change_game_mode(3, 1)
                    self.pad_x = self.WIDTH//2
                    self.powerups.clear()
                    self.balls.clear()
                    self.balls.append(Ball(self.screen, 10, self.WIDTH//2, 600, -60, self.images["balls"]["normal"]))
                else:
                    self.balls.remove(ball)
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
                    # check for side of collision
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
                    # check for type of brick
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
                    if [row, col] in self.powerups_places:
                        powerup = choice(self.POWERUP_TYPES)
                        self.powerups.append(PowerUp(self.screen, brick.X, brick.Y, self.HEIGHT, 
                                                     powerup, self.images["powerups"][powerup]))
        if not any(any(isinstance(b, Brick) and b.index!=6 for b in r) for r in self.bricks) and self.game_mode==1:
            self.game_mode = 0
            self.change_game_mode(3, 2)
    
    def init_images(self) -> None:
        """Import game images to dict"""
        self.images = {"bricks": [], "powerups": {}}
        self.images["game_gui"] = pygame.image.load(res_path(os.path.join("assets/gui", "game_gui.png")))
        for img in os.listdir(res_path(f"assets{os.path.sep}bricks")):
            self.images["bricks"].append(img)
        self.images["bricks"] = sorted(self.images["bricks"], key=lambda x: int(x.lstrip("brick").rstrip(".png")))
        self.images["bricks"].insert(0, None)
        for i, img in enumerate(self.images["bricks"]):
            if img!=None:
                self.images["bricks"][i] = pygame.image.load(res_path(os.path.join("assets/bricks", img)))

        temp = []
        for img in os.listdir(res_path(f"assets{os.path.sep}powerups")):
            temp.append(img[:-4])
            self.images["powerups"][img[:-4]] = pygame.image.load(res_path(os.path.join("assets/powerups", img)))
        self.POWERUP_TYPES = temp.copy()

        self.images["balls"] = {"normal": pygame.image.load(res_path(os.path.join("assets/balls", "ball_normal.png")))}
        self.images["pads"] = {
            "0": {
                "normal": pygame.image.load(res_path(os.path.join("assets/pads", "pad0_normal.png"))),
                "shooting": pygame.image.load(res_path(os.path.join("assets/pads", "pad0_shooting.png")))
            },
            "1": {
                "normal": pygame.image.load(res_path(os.path.join("assets/pads", "pad1_normal.png"))),
                "shooting": pygame.image.load(res_path(os.path.join("assets/pads", "pad1_shooting.png")))
            },
            "2": {
                "normal": pygame.image.load(res_path(os.path.join("assets/pads", "pad2_normal.png"))),
                "shooting": pygame.image.load(res_path(os.path.join("assets/pads", "pad2_shooting.png")))
            }
        }
                



if __name__ == "__main__":
    Game()
        