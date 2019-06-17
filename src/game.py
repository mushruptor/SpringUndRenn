import pygame
import math
import os
import sys

from pygame.locals import *
from os.path import isfile, join
from time import sleep
from enum import Enum

#TODO look into the relative paths, from where the applicaiton is launched
IMAGEDIR = "../images/"
LEVELDIR = "../levels/"

Direction = Enum('Direction', 'NEUTRAL UP DOWN LEFT RIGHT')

class Position:
    def __init__(self,x,y):
        self.X = x
        self.Y = y

class Loader:
    def load_level(self, path):
        leveldata = []
        try:
            onlyfiles = [f for f in os.listdir(path) if isfile(join(path, f))]
            for file in onlyfiles:
                try:
                    file = open(path + file)
                except Exception as e:
                    print(e)

                level = []
                for line in file:
                    line = list(map(int, line.rstrip().split(' ')))
                    level.append(line)

                leveldata.append(level)
                file.close()

        except Exception as e:
            print(e)

        return leveldata

class GameObject:
    def __init__(self, path):
        self.imagepath = path

    def load_image(self):
        self.image = pygame.image.load(self.imagepath).convert()

    def set_position(self, Pos):
        self.Pos = Pos

    def set_size(self, Size):
        self.Size

class Player(GameObject):
    direction = Direction.NEUTRAL
    speed = 10

    def __init__(self, StartPos):
        GameObject.__init__(self, IMAGEDIR + "jumper.png")
        self.Pos = StartPos

#TODO Movement specified in separate class to be inherited from
    def move_right(self):
        self.Pos.X = self.Pos.X + self.speed
        self.direction = Direction.RIGHT

    def move_left(self):
        self.Pos.X = self.Pos.X - self.speed
        self.direction = Direction.LEFT

    def move_up(self):
        self.Pos.Y = self.Pos.Y - self.speed
        self.direction = Direction.UP

    def move_down(self):
        self.Pos.Y = self.Pos.Y + self.speed
        self.direction = Direction.DOWN

    def update(self):
        pass #Part with the jumpy jumpy thing

class Window:
    def __init__(self, width, height):
        self.width = width
        self.height = height

class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self._image_surf = None

        self.loader = Loader()
        self.window = Window(800,600)
        self.player = Player(Position(20,20))

    def on_init(self):
        self.leveldata = self.loader.load_level(LEVELDIR + 'level1/')
        print(self.leveldata)

        pygame.init()
        self._display_surf = pygame.display.set_mode((self.window.width,self.window.height),pygame.HWSURFACE)

        pygame.display.set_caption('SpringUndRenn')
        self._running = True
        self.player.load_image()
        self._image_surf = self.player.image

    def on_event(self, event):
        if event.type == QUIT:
            self._running = False

    def on_loop(self):
        pass

    def on_render(self):
        self._display_surf.fill((0,0,0))
        self._display_surf.blit(self._image_surf,(self.player.Pos.X,self.player.Pos.Y))
        self.player.update()
        pygame.display.flip()
        sleep(0.03) #TODO implement Framerates

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while(self._running):
            pygame.event.pump()
            keys = pygame.key.get_pressed()

            if (keys[K_d]):
                self.player.move_right()

            if (keys[K_a]):
                self.player.move_left()

            if (keys[K_w]):
                self.player.move_up()

            if (keys[K_s]):
                self.player.move_down()

            if (keys[K_SPACE]):
                #self.player.jump()
                pass

            if (keys[K_ESCAPE]):
                self._running = False

            self.on_loop()
            self.on_render()

        self.on_cleanup()

if __name__ == "__main__":
    app = App()
    app.on_execute()
