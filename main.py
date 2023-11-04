import pygame
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
        self.bricks : list[Brick] = []
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Arkanoid")
        self.clock = pygame.time.Clock()
        self.balls.append(Ball(self.screen, (130, 130, 170), 8, 100, 500, 80))
        self.pad = Pad(self.screen, 150, 20, (150, 150, 110), self.HEIGHT/9*8)
        for i in range(10):
            for j in range(7):
                self.bricks.append(Brick(self.screen, 30+i*64, 30+j*32, (150, 150, 90)))
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

    def draw_balls_and_bricks(self) -> None:
        for ball in self.balls:
            ball.draw(1)
        for brick in self.bricks:
            brick.draw()

    def balls_collisions(self) -> None:
        for ball in self.balls:
            if ball.ball.colliderect(self.pad.pad):
                offset = (ball.coords[0]-self.mouse_x)/self.pad.WIDTH
                angle = atan(ball.power[1]/ball.power[0])
                angle2 = (pi/2-abs(angle))*(1 if angle<0 else -1)/pi
                ball.power.rotate_ip(180+180*min(max(offset+angle2, -0.5), 0.5))
                ball.coords += ball.power*3
                ball.coords[1] -= 5
            if ball.radius>=ball.coords[0] or ball.coords[0]>=self.WIDTH-ball.radius:
                ball.power[0] *= -1
            if ball.radius>=ball.coords[1] or ball.coords[1]>=self.HEIGHT-ball.radius:
                ball.power[1] *= -1
            for i, brick in enumerate(self.bricks):
                if ball.ball.colliderect(brick.brick):
                    if abs(ball.ball.bottom-brick.brick.top)<5 and ball.power[1]>0:
                        ball.power[1] *= -1
                        self.bricks.pop(i)
                    if abs(ball.ball.top-brick.brick.bottom)<5 and ball.power[1]<0:
                        ball.power[1] *= -1
                        self.bricks.pop(i)
                    if abs(ball.ball.right-brick.brick.left)<5 and ball.power[0]>0:
                        ball.power[0] *= -1
                        self.bricks.pop(i)
                    if abs(ball.ball.left-brick.brick.right)<5 and ball.power[0]<0:
                        ball.power[0] *= -1
                        self.bricks.pop(i)



if __name__ == "__main__":
    Game()
        