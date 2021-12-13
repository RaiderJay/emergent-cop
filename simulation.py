import pygame
from pygame import *
import math
import random
import sys
from config import Config

cf = Config()

unit_group = pygame.sprite.Group()
red_group = pygame.sprite.Group()
blue_group = pygame.sprite.Group()
emission_group = pygame.sprite.Group()

class Emission(pygame.sprite.Sprite):
    # This class represents a car. It derives from the "Sprite" class in Pygame.

    def __init__(self, emission_type=cf.spectrum, x_pos=0, y_pos=0, heading=cf.none):
        # Call the parent class (Sprite) constructor
        super().__init__()
        self.image = pygame.Surface([cf.unit_size*3, cf.unit_size/5])
        self.emission_type = emission_type
        self.image.fill(cf.green)
        self.rect = self.image.get_rect()
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.rect.center = [x_pos, y_pos]
        self.heading = heading
        self.age = 0
        self.attenuation = 1
        if self.emission_type == cf.thermal:
            self.attenuation = 5
            self.image.fill(cf.orange)

    def move(self, heading=(0, 1)):
        if self.age < cf.lifespan*cf.unit_size:
            self.x_pos = (self.x_pos + heading[0]) % cf.board_size
            self.y_pos = (self.y_pos + heading[1]) % cf.board_size
            self.rect.center = [self.x_pos, self.y_pos]
            self.age += self.attenuation
        else:
            self.kill()


class Unit(pygame.sprite.Sprite):
    # This class represents a car. It derives from the "Sprite" class in Pygame.

    def __init__(self, unit_type=cf.friendly, x_pos=cf.unit_size, y_pos=cf.unit_size, heading=cf.none):
        # Call the parent class (Sprite) constructor
        super().__init__()
        self.image = pygame.Surface([cf.unit_size, cf.unit_size])
        self.unit_type = unit_type
        self.image.fill(cf.blue)
        if self.unit_type == cf.enemy:
            self.image.fill(cf.red)
        self.rect = self.image.get_rect()
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.rect.center = [x_pos, y_pos]
        self.heading = heading

    def move(self, heading=(0, 1)):
        self.x_pos = (self.x_pos + heading[0]) % cf.board_size;
        self.y_pos = (self.y_pos + heading[1]) % cf.board_size;
        self.rect.center = [self.x_pos, self.y_pos]


def rect_distance(rect1, rect2):
    x1, y1 = rect1.center
    x2, y2 = rect2.center
    a = abs(x1-x2)
    b = abs(y1-y2)
    distance = math.sqrt(a**2 + b**2)
    return distance


def initialize(red_start=5, blue_start=20, separated=True):
    if separated is True:
        for i in range(blue_start):
            x_pos = random.randint(cf.unit_size, int(cf.board_size/2) - cf.unit_size*2)
            y_pos = random.randint(cf.unit_size, cf.board_size - cf.unit_size)
            heading = cf.dir_list[random.randint(1, len(cf.dir_list)-1)]
            unit = Unit(unit_type=cf.friendly, x_pos=x_pos, y_pos=y_pos, heading=heading)
            unit_group.add(unit)
            blue_group.add(unit)

        for i in range(red_start):
            x_pos = random.randint(int(cf.board_size / 2) + cf.unit_size * 2, cf.board_size - cf.unit_size)
            y_pos = random.randint(cf.unit_size, cf.board_size - cf.unit_size)
            unit = Unit(unit_type=cf.enemy, x_pos=x_pos, y_pos=y_pos)
            unit_group.add(unit)
            red_group.add(unit)

def bounce(heading):
    x = heading[0] * -1
    y = heading[1] * -1
    return (x, y)

def update():
    for unit in blue_group:
        collision = unit.rect.collidelist(unit_group.sprites())
        if(collision != -1):
            op_unit = unit_group.sprites()[collision]
            unit.heading = bounce(unit.heading)
            op_unit.heading = bounce(op_unit.heading)

    for unit in unit_group:
        unit.move(unit.heading)

    for emission in emission_group:
        emission.move(emission.heading)

    for unit in red_group:
        prop = random.randint(0, 50)
        #print(prop)
        if prop == 1:
            heading = cf.dir_list[random.randint(1, len(cf.dir_list) - 1)]
            x = unit.x_pos
            y = unit.y_pos
            emit = Emission(emission_type=cf.spectrum, x_pos=x, y_pos=y, heading=heading)
            emission_group.add(emit)
        elif prop > 30:
            heading = cf.dir_list[random.randint(1, len(cf.dir_list) - 1)]
            x = unit.x_pos
            y = unit.y_pos
            emit = Emission(emission_type=cf.thermal, x_pos=x, y_pos=y, heading=heading)
            emission_group.add(emit)


def simulate():
    # initialization
    pygame.init()
    screen = pygame.display.set_mode((1000, 1000))
    main_surface = pygame.Surface((1000, 1000))
    main_surface.fill(cf.white)

    initialize()
    clockobject = pygame.time.Clock()
    # game cycle
    while True:
        clockobject.tick(60)
        # tracking quitting
        for an_event in pygame.event.get():
            if an_event.type == QUIT:
                pygame.quit()
                sys.exit()

        screen.blit(main_surface, (0, 0))
        unit_group.draw(screen)
        emission_group.draw(screen)
        update()
        pygame.display.flip()
        pygame.display.update()


if __name__ == "__main__":
    simulate()

