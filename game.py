import pygame
import sys
import random
import time
from player import Player
from explosion import Explosion
from enemy import Enemy
from algorithm import Algorithm


import socket 
import pickle

TILE_WIDTH = 40
TILE_HEIGHT = 40

WINDOW_WIDTH = 13 * TILE_WIDTH
WINDOW_HEIGHT = 13 * TILE_HEIGHT

BACKGROUND = (107, 142, 35)

host1 = '35.234.6.168'
port1 = 5555

s = None
show_path = True

clock = None

enemy_list = []
ene_blocks = []
bombs = []
explosions = []

grid = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 2, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 2, 1],
        [1, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 2, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 2, 0, 2, 2, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 2, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

grass_img = None
block_img = None
box_img = None
bomb1_img = None
bomb2_img = None
bomb3_img = None
explosion1_img = None
explosion2_img = None
explosion3_img = None

terrain_images = []
bomb_images = []
explosion_images = []

pygame.font.init()
font = pygame.font.SysFont('Bebas', 30)
TEXT_LOSE = font.render('GAME OVER', False, (0, 0, 0))
TEXT_WIN = font.render('WIN', False, (0, 0, 0))


def game_init(path, player_alg, en1_alg, en2_alg, en3_alg, scale):

    global TILE_WIDTH
    global TILE_HEIGHT
    TILE_WIDTH = scale
    TILE_HEIGHT = scale

    global font
    font = pygame.font.SysFont('Bebas', scale)

    global show_path
    show_path = path

    global s
    s = pygame.display.set_mode((13 * TILE_WIDTH, 13 * TILE_HEIGHT))
    pygame.display.set_caption('Bomberman')

    global clock
    clock = pygame.time.Clock()

    global enemy_list
    global ene_blocks

    enemy_list = []
    ene_blocks = []
    global explosions
    global bombs
    bombs.clear()
    explosions.clear()

    global player
    player=[]
    player.append(Player(0))
    player.append(Player(1))

        
    player[0].load_animations(TILE_WIDTH)

    player[1].load_animations(TILE_WIDTH)
    global grass_img
    grass_img = pygame.image.load('images/terrain/grass.png')
    grass_img = pygame.transform.scale(grass_img, (TILE_WIDTH, TILE_HEIGHT))
    global block_img
    block_img = pygame.image.load('images/terrain/block.png')
    block_img = pygame.transform.scale(block_img, (TILE_WIDTH, TILE_HEIGHT))
    global box_img
    box_img = pygame.image.load('images/terrain/box.png')
    box_img = pygame.transform.scale(box_img, (TILE_WIDTH, TILE_HEIGHT))
    global bomb1_img
    bomb1_img = pygame.image.load('images/bomb/1.png')
    bomb1_img = pygame.transform.scale(bomb1_img, (TILE_WIDTH, TILE_HEIGHT))
    global bomb2_img
    bomb2_img = pygame.image.load('images/bomb/2.png')
    bomb2_img = pygame.transform.scale(bomb2_img, (TILE_WIDTH, TILE_HEIGHT))
    global bomb3_img
    bomb3_img = pygame.image.load('images/bomb/3.png')
    bomb3_img = pygame.transform.scale(bomb3_img, (TILE_WIDTH, TILE_HEIGHT))
    global explosion1_img
    explosion1_img = pygame.image.load('images/explosion/1.png')
    explosion1_img = pygame.transform.scale(explosion1_img, (TILE_WIDTH, TILE_HEIGHT))
    global explosion2_img
    explosion2_img = pygame.image.load('images/explosion/2.png')
    explosion2_img = pygame.transform.scale(explosion2_img, (TILE_WIDTH, TILE_HEIGHT))
    global explosion3_img
    explosion3_img = pygame.image.load('images/explosion/3.png')
    explosion3_img = pygame.transform.scale(explosion3_img, (TILE_WIDTH, TILE_HEIGHT))
    global terrain_images
    terrain_images = [grass_img, block_img, box_img, grass_img]
    global bomb_images
    bomb_images = [bomb1_img, bomb2_img, bomb3_img]
    global explosion_images
    explosion_images = [explosion1_img, explosion2_img, explosion3_img]


    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s1:
        s1.connect((host1, port1))
        main(s1)


def draw():
    s.fill(BACKGROUND)
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            s.blit(terrain_images[grid[i][j]], (i * TILE_WIDTH, j * TILE_HEIGHT, TILE_HEIGHT, TILE_WIDTH))

    for x in bombs:
        s.blit(bomb_images[x.frame], (x.posX * TILE_WIDTH, x.posY * TILE_HEIGHT, TILE_HEIGHT, TILE_WIDTH))

    for y in explosions:
        for x in y.sectors:
            s.blit(explosion_images[y.frame], (x[0] * TILE_WIDTH, x[1] * TILE_HEIGHT, TILE_HEIGHT, TILE_WIDTH))
    for p in player:
        if p.life:
            s.blit(p.animation[p.direction][p.frame],
                (p.posX * (TILE_WIDTH / 4), p.posY * (TILE_HEIGHT / 4), TILE_WIDTH, TILE_HEIGHT))

    pygame.display.update()


def generate_map():

    for i in range(1, len(grid) - 1):
        for j in range(1, len(grid[i]) - 1):
            if grid[i][j] != 0:
                continue
            elif (i < 3 or i > len(grid) - 4) and (j < 3 or j > len(grid[i]) - 4):
                continue
            if random.randint(0, 9) < 7:
                grid[i][j] = 2

    return


def main(conn):
    while player[0].life and player[1].life:
        dt = clock.tick(15)
        
        obj=pickle.loads(conn.recv(2048*128))


        temp = player[0].direction
        movement = False
        if obj['y1']>3:
            temp = 0
            player[0].move(0, 1, grid)
            movement = True
        elif obj['x1']>3:
            temp = 1
            player[0].move(1, 0, grid)
            movement = True
        elif obj['y1']<-3:
            temp = 2
            player[0].move(0, -1, grid)
            movement = True
        elif obj['x1']<-3:
            temp = 3
            player[0].move(-1, 0, grid)
            movement = True
        if temp != player[0].direction:
            player[0].frame = 0
            player[0].direction = temp
        if movement:
            if player[0].frame == 2:
                player[0].frame = 0
            else:
                player[0].frame += 1
        if obj['z1']<-5:
            if player[0].bomb_limit == 0:
                continue
            temp_bomb = player[0].plant_bomb(grid)
            bombs.append(temp_bomb)
            grid[temp_bomb.posX][temp_bomb.posY] = 3
            player[0].bomb_limit -= 1



        temp = player[1].direction
        movement = False
        if obj['y2']>3:
            temp = 0
            player[1].move(0, 1, grid)
            movement = True
        elif obj['x2']>3:
            temp = 1
            player[1].move(1, 0, grid)
            movement = True
        elif obj['y2']<-3:
            temp = 2
            player[1].move(0, -1, grid)
            movement = True
        elif obj['x2']<-3:
            temp = 3
            player[1].move(-1, 0, grid)
            movement = True
        if temp != player[1].direction:
            player[1].frame = 0
            player[1].direction = temp
        if movement:
            if player[1].frame == 2:
                player[1].frame = 0
            else:
                player[1].frame += 1
        if obj['z2']<-5:
            if player[1].bomb_limit == 0:
                continue
            temp_bomb = player[1].plant_bomb(grid)
            bombs.append(temp_bomb)
            grid[temp_bomb.posX][temp_bomb.posY] = 3
            player[1].bomb_limit -= 1
        draw()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit(0)

        update_bombs(dt)
    game_over()



def update_bombs(dt):
    for b in bombs:
        b.update(dt)
        if b.time < 1:
            b.bomber.bomb_limit += 1
            grid[b.posX][b.posY] = 0
            exp_temp = Explosion(b.posX, b.posY, b.range)
            exp_temp.explode(grid, bombs, b)
            exp_temp.clear_sectors(grid)
            explosions.append(exp_temp)
        for e in explosions:
            e.update(dt)
            if e.time < 1:
                explosions.remove(e)

def game_over():

    while True:
        dt = clock.tick(15)
        update_bombs(dt)
        count = 0
        winner = ""
        for en in enemy_list:
            en.make_move(grid, bombs, explosions, ene_blocks)
            if en.life:
                count += 1
                winner = en.algorithm.name
        if count == 1:
            draw()
            textsurface = font.render(winner + " wins", False, (0, 0, 0))
            font_w = textsurface.get_width()
            font_h = textsurface.get_height()
            s.blit(textsurface, (s.get_width() // 2 - font_w//2,  s.get_height() // 2 - font_h//2))
            pygame.display.update()
            time.sleep(2)
            break
        if count == 0:
            draw()
            textsurface = font.render("Draw", False, (0, 0, 0))
            font_w = textsurface.get_width()
            font_h = textsurface.get_height()
            s.blit(textsurface, (s.get_width() // 2 - font_w//2, s.get_height() // 2 - font_h//2))
            pygame.display.update()
            time.sleep(2)
            break
        draw()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit(0)
    explosions.clear()
    enemy_list.clear()
    ene_blocks.clear()
