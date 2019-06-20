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
MAXVELOCITY = 40

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

    def jump(self):
        if not self._jumping:
            self._jumping = True
            self.time = 0
            self.velocity = 105
            self.delta_acceleration = - self.velocity

    def update_position(self):
        dt = 1
        self.time = self.time + dt
        a_old = self.delta_acceleration
        g = self.gravity

        m = 1
        A = 1
        rho = 0.1
        c = 1

        dv = a_old * dt
        ds = 1/2 * a_old * dt
        a_new = (m * g) - (c * A * 1/2 * rho * dv)

        self.delta_acceleration = a_new

        print("a_old: ", a_old)
        print("a_new: ", a_new)
        print("dv: ", dv)
        print("ds: ", ds)
        print(" - - - ")

        self.change.y = self.change.y + ds

# the player object
class Player(GameObject,Movement):
    def __init__(self, startpos, direction=Direction.NEUTRAL, speed=10, velocity=5, gravity=10):
        GameObject.__init__(self, "jumper.png")
        self.rect = pygame.Rect((startpos.x, startpos.y),(20,20))
        self.change = self.rect.copy()
        self.speed = speed
        self.direction = direction
        self.velocity = velocity
        self.gravity = gravity

        self._jumping = False
        self.time = 0
        self.delta_acceleration = 0

    def update(self):
        print (self.x_collision, self.y_collision, self.xy_collision)
        if (self.xy_collision and not self.x_collision and not self.y_collision):
            self.change.x = self.rect.x
            self.change.y = self.rect.y
        if self.x_collision:
            self.change.x = self.rect.x
        if self.y_collision:
            self.change.y = self.rect.y
            self._jumping = False

        self.rect.x = self.change.x
        self.rect.y = self.change.y


    def collision(self, x, y, xy):
        self.x_collision = x
        self.y_collision = y
        self.xy_collision = xy

class Window:
    def __init__(self, width, height):
        self.width = width
        self.height = height

class App:
    def __init__(self):
        self._running = True
        self._display = None

        self.loader = Loader()
        self.window = Window(1000,1000)

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

        pygame.init()
        self._display = pygame.display.set_mode((self.window.width,self.window.height),pygame.HWSURFACE)
        pygame.display.set_caption('SpringUndRenn')

        self.build_static_level()

        # create the player
        self.player = Player(Position(60,20))
        self.player.load_image() # remove this later
        self.active_gameobjects.add(self.player)

        self.clock = pygame.time.Clock()

    def on_event(self, event):
        if event.type == QUIT:
            self._running = False

    # additional action which occurs each loop
    def on_loop(self):
        #gravity
        self.player.update_position()

        # colission detection
        # make hitboxes as large as the whole area covered by a move
        x_hitbox = self.player.change.copy()
        if self.player.rect.x < self.player.change.x:
            x_hitbox.x = self.player.rect.right
        else:
            x_hitbox.x = self.player.change.x
        x_hitbox.width = abs(self.player.change.x - self.player.rect.x)
        x_hitbox.y = self.player.rect.y

        y_hitbox = self.player.change.copy()
        if self.player.rect.y < self.player.change.y:
            y_hitbox.y = self.player.rect.bottom
        else:
            y_hitbox.y = self.player.change.y
        y_hitbox.height = abs(self.player.change.y - self.player.rect.y)
        y_hitbox.x = self.player.rect.x

        xy_hitbox = self.player.change.copy()

        self.player.collision(False, False, False)
        for sprite in self.passive_gameobjects:
            if x_hitbox.colliderect(sprite.rect):
                self.player.x_collision = True
            if y_hitbox.colliderect(sprite.rect):
                self.player.y_collision = True
            if xy_hitbox.colliderect(sprite.rect):
                self.player.xy_collision = True

        # update all active objects
        self.active_gameobjects.update()

    # rendering the frame
    def on_render(self):
        self._display.fill((0,0,0))

        self.active_gameobjects.draw(self._display)
        self.passive_gameobjects.draw(self._display)

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
            # if (keys[K_w]):
            #     self.player.move_up()
            # if (keys[K_s]):
            #     self.player.move_down()
            if (keys[K_SPACE]):
                self.player.jump()
            if (keys[K_ESCAPE]):
                self._running = False

            self.on_loop()
            self.on_render()

        self.on_cleanup()

if __name__ == "__main__":
    app = App()
    app.on_execute()
