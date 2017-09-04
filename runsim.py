import pygame
from random import randint

pygame.init()

size = width, height = 900, 600
black = 0, 0, 0
numTribes = 11
initRange = 50
tribes = []

worldmap = []
biomes = {}


def run():
    global worldmap, biomes
    worldmap = pygame.image.load('world-biomes-map.gif')

    biomes = {
        (0, 249, 20): "Rainforest",

    }

    for i in range(numTribes):
        tribecolor = randint(255), randint(255), randint(255)
        spawnpoint = randint()
        
        tribes.append(Tribe(i, tribecolor))


class Biome:
    def __init__(self, name, color, ):
        pass


class Tribe:
    def __init__(self, number, color):
        assert isinstance(number, int)
        self.number = number
        assert isinstance(color, tuple)
        self.color = color


class Family:
    def __init__(self, tribe):
        """

        :type tribe: Tribe
        """
        assert isinstance(tribe, Tribe)
        self.tribe = tribe

    def update(self):
        pass

    def intermarry(self):
        pass

if __name__ == "__main__":
    run()
