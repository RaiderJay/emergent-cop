import pygame
from pygame import *
import math
import random
import sys
from config import Config
from blockchain import BlockChainCop

cf = Config()
blockchain = BlockChainCop()

unit_group = pygame.sprite.Group()
red_group = pygame.sprite.Group()
blue_group = pygame.sprite.Group()
emission_group = pygame.sprite.Group()
cop_group = pygame.sprite.Group()
closest_dic = {}

class Template(pygame.sprite.Sprite):
    # This class represents a car. It derives from the "Sprite" class in Pygame.

    def __init__(self, emission_type=cf.spectrum, x_pos=0, y_pos=0, radius=100):
        # Call the parent class (Sprite) constructor
        super().__init__()
        self.image = pygame.Surface([radius, radius])
        self.emission_type = emission_type
        self.image.fill(cf.red)
        self.rect = self.image.get_rect()
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.radius = radius
        #pygame.draw.circle(self.image, cf.red, (self.x_pos, self.y_pos ), self.radius)
        self.rect.center = [x_pos, y_pos]

class Emission(pygame.sprite.Sprite):
    # This class represents a car. It derives from the "Sprite" class in Pygame.

    def __init__(self, emission_type=cf.spectrum, x_pos=0, y_pos=0, origin_unit=None, origin=(0,0), heading=cf.none):
        # Call the parent class (Sprite) constructor
        super().__init__()
        self.image = pygame.Surface([cf.unit_size*3, cf.unit_size/5])
        self.emission_type = emission_type
        self.image.fill(cf.green)
        self.rect = self.image.get_rect()
        self.origin_unit = origin_unit
        self.origin = (random.randint(origin[0]-30,origin[0]+30), random.randint(origin[1]-30,origin[1]+30))
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.rect.center = [x_pos, y_pos]
        self.heading = heading
        self.age = 0
        self.attenuation = 1
        if self.emission_type == cf.thermal:
            self.attenuation = 5
            self.image.fill(cf.orange)

    def getData(self):
        return (self.emission_type, self.origin, rect_distance(self.rect, self.origin_unit))


    def move(self, heading=(0, 1)):
        if self.age < cf.lifespan*cf.unit_size:
            x = self.x_pos + heading[0]
            y = self.y_pos + heading[1]
            if (x > (cf.board_size_x - cf.unit_size) or x < 0):  # or :
                self.heading = horizontal_bounce(heading)
                self.x_pos = self.x_pos + self.heading[0]
                self.y_pos = self.y_pos + self.heading[1]
            elif (y > (cf.board_size_y - cf.unit_size) or y < 0):
                self.heading = vertical_bounce(heading)
                self.x_pos = self.x_pos + self.heading[0]
                self.y_pos = self.y_pos + self.heading[1]
            else:
                self.x_pos = x
                self.y_pos = y
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
        self.last_heading = heading
        self.heading_lock = 0
        self.state = cf.move

    def distribute_ko(self, type, origin, radius, distance):
        blockchain.new_knowledge_object(type, origin, radius, distance)

    def get_direction(self, obj):
        x = obj.rect[0] - self.x_pos
        y = obj.rect[1] - self.y_pos
        if (x != 0):
            x = x / abs(x)
        if (y != 0):
            y = y / abs(y)
        return(x,y)


    def move(self):
        # check for collision
        unit_collision = self.rect.collidelist(blue_group.sprites())
        if(unit_collision != -1):
            bump = unit_group.sprites()[unit_collision]
            if bump != self:
                self.heading = cf.dir_list[random.randint(0, 8)]
                self.last_heading = self.heading
                self.heading_lock = 30
                # bounce and lock heading for 30 turns

        x = self.x_pos + self.heading[0]
        y = self.y_pos + self.heading[1]

        if self.state == cf.move:
            #print(self.heading)
            x = self.x_pos + self.heading[0]
            y = self.y_pos + self.heading[1]

        elif self.state == cf.attack:
            closest_list = sorted(closest_dic)
            origin = closest_dic[closest_list[0]]
            nearest_blue = []
            blue_x = []
            blue_y = []
            temp = pygame.Rect((origin[0] - cf.unit_size, origin[1] - cf.unit_size),(cf.unit_size,cf.unit_size))
            red_dist = rect_distance(self.rect, temp)
            for unit in blue_group:
                nearest_blue.append(rect_distance(self.rect, unit.rect))
                blue_x.append(unit.x_pos)
                blue_y.append(unit.y_pos)

            if sum(nearest_blue)/len(nearest_blue) < red_dist*2:
                self.heading = navigate((self.x_pos, self.y_pos), origin)
            else:
                self.heading = navigate((self.x_pos, self.y_pos),(int(sum(blue_x)/len(blue_x)),int(sum(blue_y)/len(blue_y))))
            #x = self.x_pos + self.heading[0]
            #y = self.y_pos

        if (x > (cf.board_size_x - cf.unit_size) or x < 0):
            self.heading = horizontal_bounce(self.heading)
            self.x_pos = self.x_pos + self.heading[0]
            self.y_pos = self.y_pos + self.heading[1]
        elif (y > (cf.board_size_y - cf.unit_size) or y < 0):
            self.heading = vertical_bounce(self.heading)
            self.x_pos = self.x_pos + self.heading[0]
            self.y_pos = self.y_pos + self.heading[1]

        self.x_pos = x
        self.y_pos = y
        self.rect.center = [self.x_pos, self.y_pos]




def rect_distance(rect1, rect2):
    x1, y1 = rect1.center
    x2, y2 = rect2.center
    a = abs(x1-x2)
    b = abs(y1-y2)
    distance = math.sqrt(a**2 + b**2)
    return distance


def initialize(red_start=5, blue_start=15, separated=True):
    if separated is True:
        for i in range(blue_start):
            x_pos = random.randint(cf.unit_size, int(cf.board_size_x/2) - cf.unit_size*2)
            y_pos = random.randint(cf.unit_size, cf.board_size_y - cf.unit_size)
            heading = cf.dir_list[random.randint(1, len(cf.dir_list)-1)]
            unit = Unit(unit_type=cf.friendly, x_pos=x_pos, y_pos=y_pos, heading=heading)
            unit_group.add(unit)
            blue_group.add(unit)

        for i in range(red_start):
            x_pos = random.randint(int(cf.board_size_x / 2) + cf.unit_size * 2, cf.board_size_x - cf.unit_size)
            y_pos = random.randint(cf.unit_size, cf.board_size_y - cf.unit_size)
            unit = Unit(unit_type=cf.enemy, x_pos=x_pos, y_pos=y_pos)
            unit_group.add(unit)
            red_group.add(unit)

def bounce(heading):
    x = heading[0] * -1
    y = heading[1] * -1
    return (x, y)

def vertical_bounce(heading):
    x = heading[0]
    y = heading[1] * -1
    return (x, y)

def horizontal_bounce(heading):
    x = heading[0] * -1
    y = heading[1]
    return (x, y)

def navigate(location, destination):
    x = destination[0] - location[0]
    y = destination[1] - location[1]
    if(x != 0):
        x = x/abs(x)
    if(y !=0):
        y = y/abs(y)
    return (x,y)


def blue_observe():
    for unit in blue_group:
        emit_collision = unit.rect.collidelist(emission_group.sprites())
        if(emit_collision != -1):
            emit = emission_group.sprites()[emit_collision]
            emit_type, origin, distance = emit.getData()
            unit.distribute_ko(emit_type,origin,60,distance)

def blue_orient():
    closest_list = sorted(closest_dic)
    if len(closest_list) > 0:
        for unit in blue_group:
            unit.state = cf.attack

def update():
    # Blue Observe - collect data from the collisions and update knowledge object
    blue_observe()
    # Blue Orient/decide - compute priority i.e. orient, then decide direction of the swarm
    blue_orient()
    # Blue Decide
    # Blue Act - move attack

    #first_red_unit = red_group.sprites()[0];

        #unit.heading = navigate((unit.x_pos,unit.y_pos), (first_red_unit.x_pos,first_red_unit.y_pos))

    for unit in unit_group:
        unit.move()

    for emission in emission_group:
        emission.move(emission.heading)

    ## blue kill first for initative
    for unit in blue_group:
        dist = {}
        for red_unit in red_group:
            distance = rect_distance(unit.rect, red_unit.rect)
            dist[distance] = red_unit
        distList = sorted(dist)
        if len(distList) > 0 and distList[0] < 30 :
            if (random.randint(0, 9) < 7):
                dist[distList[0]].kill()
    ## blue kill first for initative

    for unit in red_group:
        prop = random.randint(0, 100)
        #print(prop)
        if prop == 1:
            heading = cf.dir_list[random.randint(1, len(cf.dir_list) - 1)]
            x = unit.x_pos
            y = unit.y_pos
            emit = Emission(emission_type=cf.spectrum, x_pos=x, y_pos=y, origin_unit=unit.rect, origin=unit.rect.center,  heading=heading)
            emission_group.add(emit)
        elif prop > 3:
            heading = cf.dir_list[random.randint(1, len(cf.dir_list) - 1)]
            x = unit.x_pos
            y = unit.y_pos
            emit = Emission(emission_type=cf.thermal, x_pos=x, y_pos=y, origin_unit=unit.rect, origin=unit.rect.center, heading=heading)
            emission_group.add(emit)

    ## kill units one at a time for the red team update with better ranges
    ## need to update for better fire determination
        dist = {}
        for blue_unit in blue_group:
            distance = rect_distance(unit.rect, blue_unit.rect)
            dist[distance] = blue_unit
        distList = sorted(dist)
        if len(distList) > 0 and distList[0] < 32 :
            if(random.randint(0,9) < 6):
                dist[distList[0]].kill()



def simulate():
    # initialization
    pygame.init()
    screen = pygame.display.set_mode((cf.board_size_x, cf.board_size_y*2 + cf.heading*2))
    main_surface = pygame.Surface((cf.board_size_x, cf.board_size_y))
    main_surface.fill(cf.white)

    second_surface = pygame.Surface((cf.board_size_x, cf.board_size_y))
    second_surface.fill(cf.white)

    initialize()
    clockobject = pygame.time.Clock()
    # game cycle

    blockUpdate = 0;

    while True:
        clockobject.tick(60)
        # tracking quitting
        for an_event in pygame.event.get():
            if an_event.type == QUIT:
                pygame.quit()
                sys.exit()

        screen.blit(main_surface, (0, 0))
        screen.blit(second_surface, (0, cf.board_size_y + cf.heading))
        unit_group.draw(screen)
        emission_group.draw(screen)
        cop_group.draw(second_surface)
        update()
        pygame.display.flip()
        pygame.display.update()
        blockUpdate=blockUpdate+1
        if(blockUpdate == 100):
            blockchain.new_block(random.randint(1,10000))
            blockUpdate = 0

            if(len(blockchain.chain[-1]['transactions']) > 0):
                for ko in blockchain.chain[-1]['transactions']:
                    emit = ko['type']
                    x,y = ko['origin']
                    radius =  ko['radius']
                    distance = ko['radius']
                    closest_dic[distance] = (x,y)
                    cop_group.add(Template(emit,x,y,radius))
                print(blockchain.chain[-1]['transactions'])

if __name__ == "__main__":
    simulate()

