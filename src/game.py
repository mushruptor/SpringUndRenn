import pygame
import math

from pygame.locals import *
from time import sleep

class Position:
    def __init__(self,x,y):
        self.X = x
        self.Y = y

class GameObject:
    def __init__(self, path):
        self.image = pygame.image.load(path).convert()

    def set_position(self, Pos):
        self.Pos = Pos

    def set_size(self, Size):
        self.Size

class Player(GameObject):
    speed = 10

    def __init__(self, StartPos):
        self.Pos = StartPos

    def move_right(self):
        self.Pos.X = self.Pos.X + self.speed

    def move_left(self):
        self.Pos.Y = self.Pos.Y + self.speed

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

        self.window = Window(800,600)
        self.player = Player(Position(20,20))

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode((self.window.width,self.window.height),pygame.HWSURFACE)

        pygame.display.set_caption('SpringUndRenn')
        self._running = True

    def on_event(self, event):
        if event.type == QUIT:
            self._running = False

    def on_loop(self):
        pass

    def on_render(self):
        self._display_surf.fill((0,0,0))
        self._display_surf.blit(self._image_surf,(self.player.Pos.X,self.Player.Pos.Y))
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
                self.player.moveRight()

            if (keys[K_a]):
                self.player.moveLeft()

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
