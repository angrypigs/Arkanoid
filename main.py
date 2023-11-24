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
from bullet import Bullet
from custom_timer import customTimer
from utils import *


class Game:

    def __init__(self) -> None:
        # init constants and variables
        self.WIDTH = 1000
        self.HEIGHT = 700
        self.PAD_HEIGHT = self.HEIGHT//9*8
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
        self.frame_counter = 0
        self.FRAME_LIMIT = 120
        self.balls : list[Ball] = []
        self.bricks : list[list[Brick|None]] = [[None for x in range(self.COLS)] 
                                                for y in range(self.ROWS)]
        self.bullets : list[Bullet] = []
        self.powerups_places : list[list[int]] = []
        self.powerups : list[PowerUp] = []
        self.powerup_threads : list[customTimer] = [customTimer(POWERUP_TIMES[x], self.reset_powerup, [x, ]) 
                                                    for x in range(len(POWERUP_DEFAULTS))]
        self.powerup_values : list[int|bool] = list(POWERUP_DEFAULTS)
        """0 - pad length, 1 - ball speed, 2 - border, 3 - shooting pad, 4 - glue, 5 - blindness, 6 - multiplier"""
        # init pygame window
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Arkanoid")
        self.clock = pygame.time.Clock()
        self.init_images()
        # add ball and pad
        self.pad = Pad(self.screen, 120, 20, (150, 150, 110), self.PAD_HEIGHT, self.images["pads"]["0"]["normal"])
        self.pad_x = self.WIDTH//2
        # main loop
        while self.run:
            self.screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                elif event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
                    self.pause = not self.pause
                elif event.type==pygame.KEYDOWN and event.key==pygame.K_SPACE:
                    for ball in self.balls:
                        ball.glued = False
            if self.game_mode==2:
                self.game_mode = 0
                if self.current_level==self.LEVELS_AMOUNT:
                    self.current_level = 1
                else:
                    self.current_level += 1
                self.change_game_mode(3, 1)
                self.pad_x = self.WIDTH//2
                self.load_level(self.current_level)
            self.draw_game()
            self.balls_collisions()
            pygame.display.flip()
            self.frame_counter = (self.frame_counter+1)%self.FRAME_LIMIT
            self.clock.tick(self.FRAME_LIMIT)

    def change_game_mode(self, time: float, mode: int) -> None:
        def change() -> None:
            sleep(time)
            self.game_mode = mode
        Thread(target=change, daemon=True).start()

    def reset_powerup(self, index: int) -> None:
        self.powerup_values[index] = POWERUP_DEFAULTS[index]
        match index:
            case 0:
                self.pad.image = self.images["pads"]["0"]["shooting" if self.powerup_values[3] else "normal"]
                self.pad.width = 120
            case 1:
                for ball in self.balls:
                    ball.power *= (self.powerup_values[1]/ball.speed)
                    ball.speed = self.powerup_values[1]
            case 3:
                self.bullets.clear()
                self.pad.image = self.images["pads"][pad_index(self.powerup_values[0])]["normal"]
            case 4:
                for ball in self.balls:
                    ball.glued = False
            case 6:
                self.balls.sort(key=lambda y: y.coords.y)
                while len(self.balls)>1:
                    self.balls.pop()

    def brick_break(self, row: int, col: int, brick : Brick | None = None) -> None:
        """
        Take action depending of brick type and checks if it holds an powerup
        """
        if brick is None: brick = self.bricks[row][col]
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

    def load_level(self, level: int) -> None:
        """
        Loads specific level from .dat files
        """
        with open(res_path(os.path.join("levels", f"level{level}.dat")), "rb") as f:
            for line in f.readlines():
                brick_list = [[int(y) for y in x.split(":")] 
                              for x in self.fernet.decrypt(line).decode().split(";")]
        # reset all "object holders"
        self.powerups.clear()
        self.powerups_places.clear()
        self.bullets.clear()
        for i in range(7):
            self.reset_powerup(i)
        self.balls.clear()
        powerups = []
        for i in range(self.ROWS):
            for j in range(self.COLS):
                self.bricks[i][j] = None
                if brick_list[i][j]:
                    if brick_list[i][j]!=6: powerups.append([i, j])
                    self.bricks[i][j] = Brick(self.screen, 20+j*64, 50+i*32, 
                                              brick_list[i][j], self.images["bricks"][brick_list[i][j]])
        self.powerups_places.extend(sample(powerups, len(powerups)//4))
        self.balls.append(Ball(self.screen, 10, self.WIDTH//2, 600, -60, 
                               self.images["balls"]["normal"], self.powerup_values[1]))

    def draw_game(self) -> None:
        """
        Draw game components
        """
        # mouse position, shield and pad draw
        if self.powerup_values[2]: 
            self.screen.blit(self.images["effects"]["shield"], (20, self.PAD_HEIGHT+15))
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
        if not self.pause and self.game_mode==1: self.pad_x = self.mouse_x
        self.pad.draw(pygame.math.clamp(self.pad_x, 20+self.powerup_values[0]//2, self.WIDTH-20-self.powerup_values[0]//2))
        # bullets spawn and draw
        if self.powerup_values[3]:
            if self.frame_counter%60==0:
                self.bullets.append(Bullet(self.screen, self.pad.x-self.pad.width//2, 
                                           self.PAD_HEIGHT, self.COLS, self.images["effects"]["bullet"]))
                self.bullets.append(Bullet(self.screen, self.pad.x+self.pad.width//2, 
                                           self.PAD_HEIGHT, self.COLS, self.images["effects"]["bullet"]))
            for bullet in self.bullets:
                bullet.draw(not self.pause and self.game_mode==1)
        # glue draw
        if self.powerup_values[4]: 
            self.screen.blit(self.images["pads"][pad_index(self.powerup_values[0])]["glue"], 
                             (self.pad.x-self.pad.width//2, self.pad.FLAT))
        # gui draw
        self.screen.blit(self.images["game_gui"], (0, 0))
        # 
        for ball in self.balls:
            ball.draw(not self.pause and self.game_mode==1)
            if ball.glued: ball.coords.x = self.pad.x+ball.offset*self.powerup_values[0]
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
            elif power_up.mask.colliderect(self.pad.mask):
                power_up_type = power_up.type
                if power_up_type == "random":
                    power_up_type = choice([x for x in self.POWERUP_TYPES if x != "random"])
                print(power_up_type)
                index = powerup_index(power_up_type)
                new_val = powerup_value(power_up_type)
                self.powerup_values[index] = new_val
                match index:
                    case 0:
                        self.pad.image = self.images["pads"]["1" if new_val==160 else "2"]["shooting" if self.powerup_values[3] else "normal"]
                        self.pad.width = self.powerup_values[0]
                    case 1:
                        for ball in self.balls:
                            ball.power *= (new_val/ball.speed)
                            ball.speed = new_val
                    case 3:
                        self.pad.image = self.images["pads"][pad_index(self.powerup_values[0])]["shooting"]
                    case 6:
                        self.balls.sort(key=lambda y: y.coords.y)
                        for j in range(2):
                            coords = self.balls[0].coords
                            self.balls.append(Ball(self.screen, 10, coords.x, coords.y, randint(-80, -40), 
                                                   self.images["balls"]["normal"], self.powerup_values[1]))

                self.powerup_threads[index].reset()
                self.powerups.pop(i)
        for ball in self.balls:
            # pad collision
            if ball.mask.colliderect(self.pad.mask) and ball.power.y>=0:
                offset = (ball.coords.x-self.mouse_x)/self.pad.width
                angle = atan(ball.power.y/ball.power.x)
                angle2 = (pi/2-abs(angle))*(1 if angle<0 else -1)/pi
                ball.power.y *= -1
                ball.power.rotate_ip(180*min(max(offset+angle2, -0.5), 0.5))
                if ball.power.y>0: ball.power.y *= -1
                ball.coords += ball.power
                ball.coords.y -= 5
                if self.powerup_values[4]: 
                    ball.glued = True
                    ball.offset = offset
            # walls collision
            if ball.radius+20>=ball.coords.x:
                ball.power.x *= -1
                ball.coords.x = ball.radius+25
            elif ball.coords.x>=self.WIDTH-ball.radius-20:
                ball.power.x *= -1
                ball.coords.x = self.WIDTH-ball.radius-25
            if ball.radius+50>=ball.coords.y:
                ball.power.y *= -1
                ball.coords.y = ball.radius+55
            elif ball.coords.y>=ball.radius+self.PAD_HEIGHT and self.powerup_values[2]:
                ball.power.y *= -1
                ball.coords.y = self.PAD_HEIGHT-ball.radius-5
            elif ball.coords.y>=self.HEIGHT-ball.radius:
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
            b, a = int(ball.coords.x-20)//64, int(ball.coords.y-50)//32
            cells = [[x, y] for x in range(a-1, a+2) for y in range(b-2, b+3) if
                     0<=x<self.ROWS and 0<=y<self.COLS and self.bricks[x][y] is not None]
            for row, col in cells:
                brick = self.bricks[row][col]
                circle_closest_x = max(brick.X, min(ball.coords.x, brick.X + 64))
                circle_closest_y = max(brick.Y, min(ball.coords.y, brick.Y + 32))
                dist = sqrt((ball.coords.x - circle_closest_x) ** 2 + (ball.coords.y - circle_closest_y) ** 2)
                if dist < ball.radius:
                    # check for side of collision
                    overlap_x = circle_closest_x - ball.coords.x
                    overlap_y = circle_closest_y - ball.coords.y
                    if abs(overlap_x) < abs(overlap_y):
                        if overlap_y > 0 and ball.power.y>0:
                            ball.mask.bottom = brick.mask.top
                            ball.power.y *= -1
                        elif overlap_y < 0 and ball.power.y<0:
                            ball.mask.top = brick.mask.bottom
                            ball.power.y *= -1
                    else:
                        if overlap_x > 0 and ball.power.x>0:
                            ball.mask.right = brick.mask.left
                            ball.power.x *= -1
                        elif overlap_x < 0 and ball.power.x<0:
                            ball.mask.left = brick.mask.right
                            ball.power.x *= -1
                    # check for type of brick
                    self.brick_break(row, col, brick)
        for bullet in self.bullets:
            if bullet:
                col = bullet.COL
                for i in range(self.ROWS-1, -1, -1):
                    if self.bricks[i][col] is not None:
                        if bullet.mask.colliderect(self.bricks[i][col].mask):
                            self.bullets.remove(bullet)
                            self.brick_break(i, col)
                        break
            else: self.bullets.remove(bullet)

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
                "shooting": pygame.image.load(res_path(os.path.join("assets/pads", "pad0_shooting.png"))),
                "glue": pygame.image.load(res_path(os.path.join("assets/pads", "pad0_glue.png")))
            },
            "1": {
                "normal": pygame.image.load(res_path(os.path.join("assets/pads", "pad1_normal.png"))),
                "shooting": pygame.image.load(res_path(os.path.join("assets/pads", "pad1_shooting.png"))),
                "glue": pygame.image.load(res_path(os.path.join("assets/pads", "pad1_glue.png")))
            },
            "2": {
                "normal": pygame.image.load(res_path(os.path.join("assets/pads", "pad2_normal.png"))),
                "shooting": pygame.image.load(res_path(os.path.join("assets/pads", "pad2_shooting.png"))),
                "glue": pygame.image.load(res_path(os.path.join("assets/pads", "pad2_glue.png")))
            }
        }
        self.images["effects"] = {
            "shield": pygame.image.load(res_path(os.path.join("assets/effects", "barrier.png"))),
            "bullet": pygame.image.load(res_path(os.path.join("assets/effects", "bullet.png")))
        }
                



if __name__ == "__main__":
    Game()
        