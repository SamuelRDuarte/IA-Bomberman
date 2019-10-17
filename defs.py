from game import Bomb
from mapa import Map
import math
import random

def vector2dir(vx, vy):
    m = max(abs(vx), abs(vy))
    if m == abs(vx):
        if vx < 0:
            d = 'a'  # 'a'
        else:
            d = 'd'  # 'd'
    else:
        if vy > 0:
            d = 's'  # s
        else:
            d = 'w'  # w
    return d


def goto(origem, destino):
    if len(origem) != 2 or len(destino) != 2:
        return ''

    ox, oy = origem
    dx, dy = destino

    return vector2dir(dx - ox, dy - oy)

# para qualquer posicao retorna um lista de possoveis movimentos
def get_possible_ways2(mapa, position):  
    ways = []

    x, y = position
    
    if not mapa.is_blocked([x+1, y]):
        ways.append('d')
    if not mapa.is_blocked([x, y+1]):
        ways.append('s')
    if not mapa.is_blocked([x-1, y]):
        ways.append('a')
    if not mapa.is_blocked([x, y-1]):
        ways.append('w')

    return ways

def get_possible_ways(mapa, position):  
    ways = []

    x, y = position
    tile1 = mapa.get_tile((x+1,y))
    tile2 = mapa.get_tile((x-1,y))
    tile3 = mapa.get_tile((x,y+1))
    tile4 = mapa.get_tile((x,y-1))
    if tile1 != 1:
        ways.append('d')
    if tile3 != 1:
        ways.append('s')
    if tile2 != 1:
        ways.append('a')
    if tile4 != 1:
        ways.append('w')

    return ways

# da lista de possiveis caminhos escolhe o primeiro caminho
def choose_random_move(ways):
    if len(ways) != []:
        return random.choice(ways)

# dando uma key retorna a sua inversa
def inverse(key):
    if key == 'a':
        return 'd'
    elif key == 'd':
        return 'a'
    elif key == 's':
        return 'w'
    elif key == 'w':
        return 's'

# verifica se duas posicoes estao na msm direcao 
def check_same_direction(pos1, pos2):
    if len(pos1) != 2 or len(pos2) != 2:
        return False

    x1, y1 = pos1
    x2, y2 = pos2

    if x1 == x2 or y1 == y2:
        return True

    return False

# retorna distancia entre duas posiçoes
def dist_to(pos1, pos2):
    if len(pos1) != 2 or len(pos1) != 2:
        return ''

    x1, y1 = pos1
    x2, y2 = pos2

    return math.sqrt(math.pow((x2-x1), 2) + math.pow((y2-y1), 2))

# calcula e retorna a parede mais proxima (mt ineficiente)
def next_wall(bomberman_pos, walls):
    if walls == []:
        return 

    nwall = walls[0]
    min_cost = dist_to(bomberman_pos, walls[0])
    for wall in walls:
        cost = dist_to(bomberman_pos, wall)
        if cost < min_cost:
            min_cost = cost
            nwall = wall

    return nwall

def in_range(bomberman_pos,raio,obstaculo,mapa):
    cx,cy = bomberman_pos
    bx,by = obstaculo
    
    if by == cy:
        for r in range(raio + 1):
            if mapa.is_stone((bx + r, by)):
                break  # protected by stone to the right
            if (cx, cy) == (bx + r, by):
                return True
        for r in range(raio + 1):
            if mapa.is_stone((bx - r, by)):
                break  # protected by stone to the left 
            if (cx, cy) == (bx - r, by):
                return True
    if bx == cx:
        for r in range(raio + 1):
            if mapa.is_stone((bx, by + r)):
                break  # protected by stone in the bottom
            if (cx, cy) == (bx, by + r):
                return True
        for r in range(raio + 1):
            if mapa.is_stone((bx, by - r)):
                break  # protected by stone in the top
            if (cx, cy) == (bx, by - r):
                return True
    return False


def enemie_close(bomberman_pos,enimies,mapa):
    for eni in enimies:
        if in_range(bomberman_pos,2,eni['pos'],mapa):
            return True
    return False
    

def choose_hide_pos(bomberman_pos,bomb,enemies,mapa,previous_pos,tentativas):
    x,y = bomberman_pos
    if not in_range(bomberman_pos,bomb[2],bomb[0],mapa) and not enemie_close(bomberman_pos,enemies,mapa):
        return bomberman_pos
    print("checking baixo")
    if [x,y+1] != previous_pos and not mapa.is_blocked([x,y+1]):
        print("resultou baixo")
        return choose_hide_pos([x,y+1],bomb,enemies,mapa,bomberman_pos,tentativas+1)
    print("checking direita")
    if [x+1,y] != previous_pos and not mapa.is_blocked([x+1,y]):
        print("resultou direita")
        return choose_hide_pos([x+1,y],bomb,enemies,mapa,bomberman_pos,tentativas+1) 
    print("checking esquerda")
    if [x-1,y] != previous_pos and not mapa.is_blocked([x-1,y]):
        print("resultou esquerda")
        return choose_hide_pos([x-1,y],bomb,enemies,mapa,bomberman_pos,tentativas+1)
    print("checking cima")
    if [x,y-1] != previous_pos and not mapa.is_blocked([x,y-1]):
        print("resultou cima")
        return choose_hide_pos([x,y-1],bomb,enemies,mapa,bomberman_pos,tentativas+1)
        

