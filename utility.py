import pygame
from pygame import *
import math

class Utility:
    def __init__(self):
        print('utility method')

    @staticmethod
    def rect_distance(rect1, rect2):
        x1, y1 = rect1.center
        x2, y2 = rect2.center
        a = abs(x1 - x2)
        b = abs(y1 - y2)
        distance = math.sqrt(a ** 2 + b ** 2)
        return distance

    @staticmethod
    def navigate(location, destination):
        x = destination[0] - location[0]
        y = destination[1] - location[1]
        if (x != 0):
            x = x / abs(x)
        if (y != 0):
            y = y / abs(y)
        return (x, y)

    @staticmethod
    def bounce(heading):
        x = heading[0] * -1
        y = heading[1] * -1
        return (x, y)

    @staticmethod
    def vertical_bounce(heading):
        x = heading[0]
        y = heading[1] * -1
        return (x, y)

    @staticmethod
    def horizontal_bounce(heading):
        x = heading[0] * -1
        y = heading[1]
        return (x, y)

    @staticmethod
    def reduce_rect(rect_list=[]):
        return_list = []
        for suspected1 in rect_list:
            for suspected2 in rect_list:
                confirmed = suspected1.clip(suspected2)
                if confirmed.size != 0:
                    return_list.append(confirmed)
        return return_list
