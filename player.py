import pygame
import math

from bomb import Bomb

class Player:

    

    def __init__(self,p):
        self.life = True
        self.p=p
        if self.p==0:
            self.posX = 4
            self.posY = 4
        elif self.p==1:
            self.posX = 44
            self.posY = 44
        self.direction = 0
        self.frame = 0
        self.animation = []
        self.range = 3
        self.bomb_limit = 2
    def move(self, dx, dy, grid):
        tempx = int(self.posX/4)
        tempy = int(self.posY/4)

        map = []

        for i in range(len(grid)):
            map.append([])
            for j in range(len(grid[i])):
                map[i].append(grid[i][j])

        if self.posX % 4 != 0 and dx == 0:
            if self.posX % 4 == 1:
                self.posX -= 1
            elif self.posX % 4 == 3:
                self.posX += 1
            return
        if self.posY % 4 != 0 and dy == 0:
            if self.posY % 4 == 1:
                self.posY -= 1
            elif self.posY % 4 == 3:
                self.posY += 1
            return

        # right
        if dx == 1:
            if map[tempx+1][tempy] == 0:
                self.posX += 1
        # left
        elif dx == -1:
            tempx = math.ceil(self.posX / 4)
            if map[tempx-1][tempy] == 0:
                self.posX -= 1

        # bottom
        if dy == 1:
            if map[tempx][tempy+1] == 0:
                self.posY += 1
        # top
        elif dy == -1:
            tempy = math.ceil(self.posY / 4)
            if map[tempx][tempy-1] == 0:
                self.posY -= 1

    def plant_bomb(self, map):
        b = Bomb(self.range, round(self.posX/4), round(self.posY/4), map, self)
        return b

    def check_death(self, exp):
        for e in exp:
            for s in e.sectors:
                if int(self.posX/4) == s[0] and int(self.posY/4) == s[1]:
                    self.life = False

    def load_animations(self, scale):
        front = []
        back = []
        left = []
        right = []
        resize_width = scale
        resize_height = scale
        if self.p==0:
            f1 = pygame.image.load('images/hero/pf0.png')
            f2 = pygame.image.load('images/hero/pf1.png')
            f3 = pygame.image.load('images/hero/pf2.png')
        elif self.p==1:
            f1 = pygame.image.load('images/enemy/e1f0.png')
            f2 = pygame.image.load('images/enemy/e1f1.png')
            f3 = pygame.image.load('images/enemy/e1f2.png')

        f1 = pygame.transform.scale(f1, (resize_width, resize_height))
        f2 = pygame.transform.scale(f2, (resize_width, resize_height))
        f3 = pygame.transform.scale(f3, (resize_width, resize_height))

        front.append(f1)
        front.append(f2)
        front.append(f3)
        if self.p==0:
            r1 = pygame.image.load('images/hero/pr0.png')
            r2 = pygame.image.load('images/hero/pr1.png')
            r3 = pygame.image.load('images/hero/pr2.png')
        elif self.p==1:
            r1 = pygame.image.load('images/enemy/e1r0.png')
            r2 = pygame.image.load('images/enemy/e1r1.png')
            r3 = pygame.image.load('images/enemy/e1r2.png')
        r1 = pygame.transform.scale(r1, (resize_width, resize_height))
        r2 = pygame.transform.scale(r2, (resize_width, resize_height))
        r3 = pygame.transform.scale(r3, (resize_width, resize_height))

        right.append(r1)
        right.append(r2)
        right.append(r3)
        if self.p==0:
            b1 = pygame.image.load('images/hero/pb0.png')
            b2 = pygame.image.load('images/hero/pb1.png')
            b3 = pygame.image.load('images/hero/pb2.png')
        elif self.p==1:
            b1 = pygame.image.load('images/enemy/e1b0.png')
            b2 = pygame.image.load('images/enemy/e1b1.png')
            b3 = pygame.image.load('images/enemy/e1b2.png')
        b1 = pygame.transform.scale(b1, (resize_width, resize_height))
        b2 = pygame.transform.scale(b2, (resize_width, resize_height))
        b3 = pygame.transform.scale(b3, (resize_width, resize_height))

        back.append(b1)
        back.append(b2)
        back.append(b3)
        if self.p==0:
            l1 = pygame.image.load('images/hero/pl0.png')
            l2 = pygame.image.load('images/hero/pl1.png')
            l3 = pygame.image.load('images/hero/pl2.png')
        elif self.p==1:
            l1 = pygame.image.load('images/enemy/e1l0.png')
            l2 = pygame.image.load('images/enemy/e1l1.png')
            l3 = pygame.image.load('images/enemy/e1l2.png')
        l1 = pygame.transform.scale(l1, (resize_width, resize_height))
        l2 = pygame.transform.scale(l2, (resize_width, resize_height))
        l3 = pygame.transform.scale(l3, (resize_width, resize_height))

        left.append(l1)
        left.append(l2)
        left.append(l3)

        self.animation.append(front)
        self.animation.append(right)
        self.animation.append(back)
        self.animation.append(left)
