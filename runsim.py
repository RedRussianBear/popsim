import sys
import time
from random import randint

import pygame

pygame.init()

black = 0, 0, 0
rate = 60.0
wait = 1.0 / rate

num_clans = 11
init_range = 50

worldmap = []
biomes = {}
clans = []
families = []

direct = [
    (-1, 0),
    (1, 0),
    (0, 1),
    (0, -1),
]

color_to_biome = {
    (0, 148, 255, 255): 'Ocean',
    (164, 215, 252, 255): 'Freshwater',
    (0, 249, 20, 255): 'Rainforest',
    (0, 187, 89, 255): 'Forest',
    (0, 136, 124, 255): 'Taiga',
    (255, 152, 0, 255): 'Savanna',
    (230, 252, 121, 255): 'Grassland',
    (255, 213, 0, 255): 'Desert',
    (151, 253, 248, 255): 'Tundra',
    (255, 255, 255, 255): 'Ice',
}


def run():
    global worldmap, biomes, clans, families
    biomes = {
        'Ocean': Biome('Ocean', 2, 50),
        'Freshwater': Biome('Freshwater', 20, 2),
        'Rainforest': Biome('Rainforest', 10, 10),
        'Forest': Biome('Forest', 15, 5),
        'Taiga': Biome('Taiga', 10, 8),
        'Savanna': Biome('Savanna', pygame.Color(255, 152, 0), 15, 0),
        'Grassland': Biome('Grassland', pygame.Color(230, 252, 121), 20, 0),
        'Desert': Biome('Desert', pygame.Color(255, 213, 0), 3, 0),
        'Tundra': Biome('Tundra', pygame.Color(151, 253, 248), 5, 2),
        'Ice': Biome('Ice', pygame.Color(255, 255, 255), 0, 0),
    }

    worldmap_image = pygame.image.load('world-map.png')
    worldrect = worldmap_image.get_rect()
    size = max_long, max_lat = worldmap_image.get_size()

    for lat in range(max_lat):
        current_lat = []
        worldmap.append(current_lat)
        for long in range(max_long):
            pixel = worldmap_image.get_at((long, lat))
            current_lat.append(Plot(color_to_biome[(pixel.r, pixel.g, pixel.b, pixel.a)], (lat, long)))

    for i in range(num_clans):
        clan_color = pygame.Color(randint(0, 255), randint(0, 255), randint(0, 255), 255)
        spawn_point = spawn_lat, spawn_long = randint(0, max_lat), randint(0, max_long)

        while worldmap[spawn_lat][spawn_long].biome.difficulty > 10:
            spawn_point = spawn_lat, spawn_long = (spawn_lat + 10) % max_lat, (spawn_long + 10) % max_long

        new_clan = Clan(i, clan_color, spawn_point)
        new_family = Family(new_clan, spawn_point)

        worldmap[spawn_lat][spawn_long].occupant = new_family

        families.append(new_family)
        clans.append(new_clan)

    screen = pygame.display.set_mode(size)

    while True:
        timer = time.clock()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        for lat in range(max_lat):
            for long in range(max_long):
                worldmap[lat][long].update()

        for family in families:
            family.update()

        families = [family for family in families if family.strength > 1]
        print('Time spent doing logic: ' + str(time.clock() - timer))

        timer = time.clock()
        screen.blit(worldmap_image, worldrect)
        for family in families:
            screen.set_at((family.long, family.lat), family.tribe.color)

        pygame.display.flip()
        print('Time spent doing graphics: ' + str(time.clock() - timer))
        time.sleep(wait)


class Plot:
    def __init__(self, biomeid, location):
        assert isinstance(biomeid, str)
        assert isinstance(location, tuple)

        self.biome, self.location = biomes[biomeid], location
        self.lat, self.long = self.location
        self.capacity, self.max_capacity = self.biome.capacity, self.biome.capacity
        self.occupant = 0

    def update(self):
        new_val = self.capacity + 0.2 * self.max_capacity
        self.capacity = new_val if new_val < self.max_capacity else self.max_capacity

    def improve(self):
        if self.max_capacity == self.biome.capacity * 2: return
        self.max_capacity = self.max_capacity * 1.5 if self.max_capacity * 1.5 < self.biome.capacity * 2 else self.biome.capacity * 2


class Biome:
    def __init__(self, name, capacity, difficulty):
        self.name, self.color, self.capacity, self.difficulty = name, color, capacity, difficulty


class Clan:
    def __init__(self, number, color, spawn):
        assert isinstance(number, int)
        assert isinstance(color, pygame.Color)
        assert isinstance(spawn, tuple)
        self.number, self.color, self.spawn = number, color, spawn


class Family:
    def __init__(self, tribe, position):
        assert isinstance(tribe, Clan)
        self.tribe, self.position = tribe, position
        self.lat, self.long = self.position
        self.strength = 8
        self.energy = 8

    def update(self):
        plot = worldmap[self.lat][self.long]

        self.strength *= 1.5
        plot.improve()

        if self.strength > plot.capacity:
            for direction in direct:
                new_lat = self.lat + direction[0]
                new_long = self.long + direction[1]
                new_plot = worldmap[new_lat][new_long]
                if new_plot.occupant == 0 and self.strength > 4:
                    new_family = Family(self.tribe, (new_lat, new_long))
                    new_family.strength = self.strength / 2
                    new_family.energy = new_family.strength - new_plot.biome.difficulty
                    self.strength /= 2
                    families.append(new_family)
                    new_plot.occupant = new_family
                    break

        consume = self.strength
        energy = self.strength

        plot.capacity, consume = plot.capacity - consume if plot.capacity - consume > 0 else 0, \
                                 consume - plot.capacity if consume - plot.capacity > 0 else 0

        while consume > 0 and energy > 0:
            energy = self.wander(energy)
            plot = worldmap[self.lat][self.long]
            plot.capacity, consume = plot.capacity - consume if plot.capacity - consume > 0 else 0, \
                                     consume - plot.capacity if consume - plot.capacity > 0 else 0

        if consume > 0:
            self.strength -= consume

        self.energy = self.strength

    def wander(self, energy):
        max_capacity = -1
        max_direct = ()

        for direction in direct:
            new_lat = self.lat + direction[0]
            new_long = self.long + direction[1]
            new_plot = worldmap[new_lat][new_long]
            if new_plot.capacity > max_capacity and new_plot.biome.difficulty <= energy:
                max_capacity = new_plot.capacity
                max_direct = direction

        if max_capacity > 0:
            worldmap[self.lat][self.long].occupant = 0
            self.position = self.lat, self.long = self.lat + max_direct[0], self.long + max_direct[1]
            worldmap[self.lat][self.long].occupant = self
            return energy - worldmap[self.lat][self.long].biome.difficulty
        else:
            return -1

    def intermarry(self):
        pass


if __name__ == "__main__":
    run()
