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
SQUARESIZE = 20

Direction = Enum('Direction', 'NEUTRAL UP DOWN LEFT RIGHT')

class Position:
    def __init__(self,x,y):
        self.x = x
        self.y = y

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

class GameObject(pygame.sprite.Sprite):
    def __init__(self, path, pos=Position(0,0)):
        pygame.sprite.Sprite.__init__(self)
        self.imagepath = IMAGEDIR + path
        self.load_image()

        #set the initial position of the object
        self.rect = self.image.get_rect()
        self.set_position(pos)

    def load_image(self):
        # if you want animated pictures, load a list of images and iterate
        # through them each frame you call the update method of an object which
        # derived from this class
        self.image = pygame.image.load(self.imagepath).convert()

    def set_position(self, pos):
        self.rect.x = pos.x
        self.rect.y = pos.y

    def set_size(self, size):
        self.Size = size

class Block(GameObject):
    def __init__(self, path, pos, left=1, right=1, top=1, bottom=1):
        GameObject.__init__(self, path, pos)

        # tells if the object is solid in one or more directions. 1 marks solid
        # and 0 marks non-solid
        self.LEFT = left
        self.RIGHT = right
        self.TOP = top
        self.BOTTOM = bottom

class Stone(Block):
    def __init__(self, pos):
        Block.__init__(self, "stone.png", pos)

# movement interface
class Movement:
    def move_right(self):
        self.change.x = self.rect.x + self.speed
        self.direction = Direction.RIGHT

    def move_left(self):
        self.change.x = self.rect.x - self.speed
        self.direction = Direction.LEFT

    def move_up(self):
        self.change.y = self.rect.y - self.speed
        self.direction = Direction.UP

    def move_down(self):
        self.change.y = self.rect.y + self.speed
        self.direction = Direction.DOWN

# the player object
class Player(GameObject,Movement):
    def __init__(self, startpos, direction=Direction.NEUTRAL, speed=10, velocity=5):
        GameObject.__init__(self, "jumper.png")
        self.rect = pygame.Rect((startpos.x, startpos.y),(20,20))
        self.change = self.rect.copy()
        self.speed = speed
        self.direction = direction
        self.velocity = velocity

    def update(self):
        if not self.LEFT and self.rect.x > self.change.x:
            self.rect.x = self.change.x
        if not self.RIGHT and self.rect.x < self.change.x:
            self.rect.x = self.change.x
        if not self.TOP and self.rect.y > self.change.y:
            self.rect.y = self.change.y
        if not self.BOTTOM and self.rect.y < self.change.y:
            self.rect.y = self.change.y

    def colission(self, left, right, top, bottom):
        self.LEFT = left
        self.RIGHT = right
        self.TOP = top
        self.BOTTOM = bottom


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

        # list to keep track of alle the objects, which have to be updated
        self.active_gameobjects = pygame.sprite.Group()
        # don't have to be updated every iteration
        self.passive_gameobjects = pygame.sprite.Group()

    def build_static_level(self):
        y_off = 0
        for line in self.leveldata[1]:
            x_off = 0
            for obj in line:
                block = None

                if obj == 1:
                    block = Stone(Position(x_off,y_off))

                if block != None:
                    block.load_image()
                    self.passive_gameobjects.add(block)

                x_off = x_off + SQUARESIZE
            y_off = y_off + SQUARESIZE

    def on_init(self):
        #TODO remove: just to test the leveldata
        self.leveldata = self.loader.load_level(LEVELDIR + 'level1/')
        print(self.leveldata)

        pygame.init()
        self._display_surf = pygame.display.set_mode((self.window.width,self.window.height),pygame.HWSURFACE)
        pygame.display.set_caption('SpringUndRenn')

        self.build_static_level()

        # create the player
        self.player = Player(Position(20,20))
        self.player.load_image() # remove this later
        self.active_gameobjects.add(self.player)

        # create some dummy stones
        # stone = Stone(Position(200,200))
        # stone.load_image() # remove this later
        # self.passive_gameobjects.add(stone)

        self.clock = pygame.time.Clock()

    def on_event(self, event):
        if event.type == QUIT:
            self._running = False

    # additional action which occurs each loop
    def on_loop(self):
        # colission detection
        hitbox = pygame.Rect((self.player.rect.x - 2, self.player.rect.y - 2), (24,24))

        self.player.colission(False, False, False, False)
        for sprite in self.passive_gameobjects:
            if hitbox.colliderect(sprite.rect):
                print(sprite.rect)

                # would be better to only check on move
                # TODO check if Block is solid
                if sprite.rect.collidepoint(hitbox.midleft):
                    self.player.LEFT = True
                if sprite.rect.collidepoint(hitbox.midright):
                    self.player.RIGHT = True
                if sprite.rect.collidepoint(hitbox.midtop):
                    self.player.TOP = True
                if sprite.rect.collidepoint(hitbox.midbottom):
                    self.player.BOTTOM = True


        # update all active objects
        self.active_gameobjects.update()

    # rendering the frame
    def on_render(self):
        self._display_surf.fill((0,0,0))

        self.active_gameobjects.draw(self._display_surf)
        self.passive_gameobjects.draw(self._display_surf)

        pygame.display.flip()
        self.clock.tick(30)

    # actions on shutting the program down
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
