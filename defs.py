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
    print("tijolos")
    print(tile1)
    print(tile2)
    print(tile3)
    print(tile4)
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
