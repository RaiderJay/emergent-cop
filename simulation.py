import pygame
from pygame import *
import random
import sys
from config import Config
from blockchain import BlockChainCop
from utility import Utility

cf = Config()
blockchain = BlockChainCop()
util = Utility()

unit_group = pygame.sprite.Group()
red_group = pygame.sprite.Group()
blue_group = pygame.sprite.Group()
emission_group = pygame.sprite.Group()
cop_group = pygame.sprite.Group()
closest_dic = {}



class KO(pygame.sprite.Sprite):
    # This class represents a car. It derives from the "Sprite" class in Pygame.

    def __init__(self, emission_type=cf.spectrum, x_pos=0, y_pos=0, radius=100):
        # Call the parent class (Sprite) constructor
        super().__init__()

        self.image = pygame.Surface([radius, radius])
        self.emission_type = emission_type
        self.image.fill(cf.green)
        if self.emission_type == cf.thermal:
            self.image.fill(cf.orange)
        elif self.emission_type == cf.visual:
            self.image.fill(cf.red)
        elif self.emission_type == cf.red_kill:
            self.image.fill(cf.black)

        self.rect = self.image.get_rect()
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.radius = radius
        #pygame.draw.circle(self.image, cf.red, (self.x_pos, self.y_pos ), self.radius)
        self.rect.center = [x_pos, y_pos]
        self.life_span = cf.cop_spectrum_lifespan
        if self.emission_type == cf.thermal:
            self.life_span = cf.cop_thermal_lifespan
        elif self.emission_type == cf.visual:
            self.life_span = cf.cop_visual_lifespan
        elif self.emission_type == cf.red_kill:
            self.life_span = cf.cop_kill_lifespan

    def move(self):
        self.life_span = self.life_span - 1
        if self.life_span < 1:
            self.kill()

class Emission(pygame.sprite.Sprite):
    # This class represents a car. It derives from the "Sprite" class in Pygame.

    def __init__(self, emission_type=cf.spectrum, x_pos=0, y_pos=0, origin_unit=None, origin=(0,0), heading=cf.none):
        # Call the parent class (Sprite) constructor
        super().__init__()
        self.image = pygame.Surface([1, 1])#[cf.unit_size*3, cf.unit_size/5])
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
        rad = cf.spectrum_radius
        if self.emission_type == cf.thermal:
            rad = cf.thermal_radius
        if self.emission_type == cf.visual:
            rad = cf.visual_radius
        return (self.emission_type, self.origin, rad, util.rect_distance(self.rect, self.origin_unit))


    def move(self, heading=(0, 1)):
        if self.age < cf.lifespan*cf.unit_size:
            if cf.lifespan*cf.unit_size % 100 ==0:
                if self.heading == cf.E or self.heading == cf.W:
                    self.image = pygame.transform.scale(self.image,(self.image.get_width(), self.image.get_height() + 1))
                else:
                    self.image = pygame.transform.scale(self.image, (self.image.get_width()+1, self.image.get_height()))
            x = self.x_pos + heading[0]
            y = self.y_pos + heading[1]

            self.x_pos = x
            self.y_pos = y
            self.rect.center = [self.x_pos, self.y_pos]
            self.age += self.attenuation
        else:
            self.kill()

class ADA(pygame.sprite.Sprite):
    def __init__(self, unit_type=cf.friendly, x_pos=cf.unit_size, y_pos=cf.unit_size, heading=cf.none):
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

class Unit(pygame.sprite.Sprite):
    # This class represents a car. It derives from the "Sprite" class in Pygame.

    def __init__(self, unit_type=cf.friendly, x_pos=cf.unit_size, y_pos=cf.unit_size, heading=cf.none):
        # Call the parent class (Sprite) constructor
        super().__init__()
        blue_drone = pygame.image.load('./images/blue_drone.png').convert_alpha()
        red_ada = pygame.image.load('./images/red_ada.png').convert_alpha()
        self.image = blue_drone
        #self.image = pygame.Surface([cf.unit_size, cf.unit_size])
        self.unit_type = unit_type
        #self.image.fill(cf.blue)
        if self.unit_type == cf.enemy:
            self.image.fill(cf.red)
            self.image = red_ada
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

    def fire(self):
        # get number to determine if hit or miss
        prob = random.randint(0, 100)
        dist = {}

        # actions for friendly units
        if self.unit_type == cf.friendly:
            for red_unit in red_group:
                distance = util.rect_distance(self.rect, red_unit.rect)
                dist[distance] = red_unit
                distList = sorted(dist)
                if len(distList) > 0 and distList[0] < cf.blue_range:
                    if prob < cf.blue_accuracy:
                        dist[distList[0]].kill()
                        closest_dic.clear()
                        self.distribute_ko(cf.red_kill,dist[distList[0]].rect.center,cf.visual_radius,distList[0])
                        for unit in blue_group:
                            unit.state = cf.disperse

        # actions for hostile units
        else:
            for blue_unit in blue_group:
                distance = util.rect_distance(self.rect, blue_unit.rect)
                dist[distance] = blue_unit
                distList = sorted(dist)
                if len(distList) > 0 and distList[0] < cf.red_range:
                    if prob < cf.red_accuracy:
                        dist[distList[0]].kill()

    def smart_bump(self):
        prob = random.randint(0,3)
        self.state = cf.move
        self.heading_lock = 10

        if self.heading == cf.N or self.heading == cf.S:
            if prob > 1:
                self.heading = cf.E
            else:
                self.heading = cf.W
        elif self.heading == cf.E or self.heading == cf.W:
            if prob > 1:
                self.heading = cf.N
            else:
                self.heading = cf.S
        elif self.heading == cf.NE:
            if prob == 0:
                self.heading = cf.N
            else:
                self.heading = cf.E
        elif self.heading == cf.SE:
            if prob == 0:
                self.heading = cf.E
            else:
                self.heading = cf.S
        elif self.heading == cf.NW:
            if prob == 0:
                self.heading = cf.N
            else:
                self.heading = cf.W
        elif self.heading == cf.SW:
            if prob == 0:
                self.heading = cf.W
            else:
                self.heading = cf.S

        else:
            self.heading = cf.E

    def collide(self):
        unit_collision = self.rect.collidelist(blue_group.sprites())
        if unit_collision != -1:
            bump = unit_group.sprites()[unit_collision]
            if bump != self:
                if self.state != cf.attack:
                    self.heading = cf.dir_list[random.randint(0, 8)]
                    self.last_heading = self.heading
                else:
                    self.smart_bump()

    def space(self):
        for unit in blue_group:
            if unit != self:
                if util.rect_distance(self.rect, unit.rect) < 20:
                    unit.smart_bump()
                    self.smart_bump()
                    break;


    def get_attack_heading(self):
        closest = {key: val[1] for key, val in closest_dic.items() if val[1] != cf.red_kill}
        if(len(closest) > 0 or len(closest_dic) > 0):
            closest_list = sorted(closest)
            origin = closest_dic[closest_list[0]][0]
            origin_rect = pygame.Rect((origin[0] - cf.unit_size, origin[1] - cf.unit_size), (cf.unit_size, cf.unit_size))
            distance_to_tgt = util.rect_distance(self.rect, origin_rect)
            neighbor_distance_tgt = []

            for unit in blue_group:
                neighbor_distance_tgt.append(util.rect_distance(unit.rect, origin_rect))

            ave_dist = sum(neighbor_distance_tgt) / len(neighbor_distance_tgt)
            if distance_to_tgt < cf.red_range: # or len(blue_group.sprites()) < 2:  # bum rush
                self.heading = util.navigate((self.x_pos, self.y_pos), origin)
            elif len(blue_group) == 1:
                self.heading = util.navigate((self.x_pos, self.y_pos), origin) # lst one bum rush
            elif distance_to_tgt == cf.red_range+1:
                self.heading = (0, 0)
            elif all(x < distance_to_tgt for x in neighbor_distance_tgt):  # if neighbors are near attack
                self.heading = util.navigate((self.x_pos, self.y_pos), origin)
            elif distance_to_tgt > ave_dist:  # Catch up
                    self.heading = util.navigate((self.x_pos, self.y_pos), origin)
            else:
                self.heading = (0, 0)  # wait
        else:
            for unit in blue_group:
                unit.state = cf.disperse
    def move(self):

        #check for collisions

        x = self.x_pos + self.heading[0]
        y = self.y_pos + self.heading[1]

        if self.state == cf.attack:
            self.get_attack_heading()
        elif self.state == cf.disperse:
            self.heading = cf.dir_list[random.randint(1,8)]
            self.state = cf.move
            self.heading_lock = 100
        else:
            self.heading_lock = self.heading_lock - 1

        if self.state == cf.attack:
            self.space()
        else:
            self.collide()

        if (x > (cf.board_size_x - cf.unit_size) or x < 0):
            self.heading = util.horizontal_bounce(self.heading)
            self.x_pos = self.x_pos + self.heading[0]
            self.y_pos = self.y_pos + self.heading[1]
        elif (y > (cf.board_size_y - cf.unit_size) or y < 0):
            self.heading = util.vertical_bounce(self.heading)
            self.x_pos = self.x_pos + self.heading[0]
            self.y_pos = self.y_pos + self.heading[1]

        self.x_pos = x
        self.y_pos = y


        self.rect.center = [self.x_pos, self.y_pos]
        self.fire()

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

def blue_observe():
    for unit in blue_group:
        emit_collision = unit.rect.collidelist(emission_group.sprites())
        if(emit_collision != -1):
            emit = emission_group.sprites()[emit_collision]
            emit_type, origin, radius, distance = emit.getData()

            unit.distribute_ko(emit_type,origin,radius,distance)

def blue_orient():

    #closest_list = sorted(closest)
    if len(closest_dic) > 0:
        #print("attack")
        for unit in blue_group:
            if unit.heading_lock < 1:
                #print('attack')
                unit.state = cf.attack

def update():
    # Blue Observe - collect data from the collisions and update knowledge object
    blue_observe()
    # Blue Orient/decide - compute priority i.e. orient, then decide direction of the swarm
    blue_orient()

    for unit in unit_group:
        unit.move()

    for icon in cop_group:
        icon.move()

    for emission in emission_group:
        emission.move(emission.heading)

    for unit in red_group:
        prop = random.randint(0, 100)
        #print(prop)
        if prop < 4:
            heading = cf.dir_list[random.randint(1, len(cf.dir_list) - 1)]
            x = unit.x_pos
            y = unit.y_pos
            emit = Emission(emission_type=cf.spectrum, x_pos=x, y_pos=y, origin_unit=unit.rect, origin=unit.rect.center,  heading=heading)
            emission_group.add(emit)
        if prop < 30:
            heading = cf.dir_list[random.randint(1, len(cf.dir_list) - 1)]
            x = unit.x_pos
            y = unit.y_pos
            emit = Emission(emission_type=cf.thermal, x_pos=x, y_pos=y, origin_unit=unit.rect, origin=unit.rect.center, heading=heading)
            emission_group.add(emit)

def simulate():
    # initialization
    pygame.init()
    screen = pygame.display.set_mode((cf.board_size_x, cf.board_size_y*2 + cf.heading*2))
    #screen = pygame.display.set_mode((cf.board_size_x, cf.board_size_y*2 + cf.heading*2), FULLSCREEN, 32)
    main_surface = pygame.Surface((cf.board_size_x, cf.board_size_y))
    main_surface.fill(cf.white)

    second_surface = pygame.Surface((cf.board_size_x, cf.board_size_y))
    second_surface.fill(cf.white)

    initialize(red_start=cf.red_start_set,blue_start=cf.blue_start_set)
    clockobject = pygame.time.Clock()
    # game cycle

    blockUpdate = 0;
    blockUpdate1 = 0;
    font = pygame.font.Font(pygame.font.get_default_font(), 12)
    title = pygame.font.Font(pygame.font.get_default_font(), 24)
    #textsurface = font.render(str(len(blue_group)), False, (0, 0, 0))

    while True:
        clockobject.tick(120)
        # tracking quitting
        for an_event in pygame.event.get():
            if an_event.type == QUIT:
                pygame.quit()
                sys.exit()

        screen.blit(main_surface, (0, cf.heading ))
        screen.blit(second_surface, (0, cf.board_size_y + cf.heading*2))
        main_surface.fill(cf.white)
        second_surface.fill(cf.white)

        main_title = title.render("Combat", False, (255, 255, 255))
        main_rect = main_title.get_rect(center=(cf.board_size_x/2, cf.heading /2))
        screen.blit(main_title, main_rect)

        blue_unit_text = font.render(  "BLUE UNITS:  " + str(len(blue_group)), False, (0, 0, 0))
        screen.blit(blue_unit_text,(10,cf.heading + 10))
        red_unit_text = font.render(  "RED UNITS:    " + str(len(red_group)), False, (0, 0, 0))
        screen.blit(red_unit_text,(10,cf.heading + 30))

        cop_title = title.render("Emergent Common Operating Picture", False, (255, 255, 255))
        cop_rect = cop_title.get_rect(center=(cf.board_size_x/2, cf.board_size_y + cf.heading + cf.heading/2))
        screen.blit(cop_title, cop_rect)

        count = 0
        for line in blockchain.chain[-1]['transactions']:
            textblock = font.render(str(line), False, (0, 0, 0))
            screen.blit(textblock, (0, cf.board_size_y + cf.heading*2 + count))
            count += 10


        emission_group.draw(main_surface)
        unit_group.draw(main_surface)
        cop_group.draw(second_surface)
        pygame.display.flip()
        pygame.display.update()

        update()

        blockUpdate=blockUpdate+1
        blockUpdate1 = blockUpdate1 + 1
        if(blockUpdate == 100):
            blockchain.new_block(random.randint(1,10000))
            blockUpdate = 0

            if(len(blockchain.chain[-1]['transactions']) > 0):
                for ko in blockchain.chain[-1]['transactions']:
                    emit = ko['type']
                    x,y = ko['origin']
                    radius =  ko['radius']
                    distance = ko['radius']
                    closest_dic[distance] = ((x,y), emit)
                    new_icon = KO(emit, x, y, radius)
                    cop_group.add(new_icon)
                print(blockchain.chain[-1]['transactions'])
        if (blockUpdate1 == 2500):
            blockUpdate1 = 0
            closest_dic.clear()

if __name__ == "__main__":
    simulate()

