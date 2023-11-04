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
        self.balls.append(Ball(self.screen, (130, 130, 170), 8, 100, 100, 80))
        self.pad = Pad(self.screen, 150, 20, (150, 150, 110), self.HEIGHT/4*3)
        # for i in range(10):
        #     for j in range(7):
        #         self.bricks.append(Brick(self.screen, ))
        while self.run:
            self.screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
            self.mouse_x, mouse_y = pygame.mouse.get_pos()
            self.pad.draw(pygame.math.clamp(self.mouse_x, 75, self.WIDTH-75))
            self.balls_collisions()
            pygame.display.flip()
            self.clock.tick(120)

    def balls_collisions(self) -> None:
        for ball in self.balls:
            ball.draw(1)
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

if __name__ == "__main__":
    Game()
        