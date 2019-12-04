from mapa import Map
import math
import random


def find_corner(mapa):
    for x in range(mapa.hor_tiles):
        for y in range(mapa.ver_tiles):
            if not mapa.is_blocked((x, y)):
                return (x, y)

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
    
    tile1 = mapa.map[x+1][y]
    tile2 = mapa.map[x-1][y]
    tile3 = mapa.get_tile((x,y+1))
    tile4 = mapa.get_tile((x,y-1))

    if tile1 != 1 and not (x+1,y) in mapa.walls:
        ways.append('d')
    if tile3 != 1 and not (x,y+1) in mapa.walls:
        ways.append('s')
    if tile2 != 1 and not (x-1,y) in mapa.walls:
        ways.append('a')
    if tile4 != 1 and not (x,y-1) in mapa.walls:
        ways.append('w')

    return ways


# retorna distancia entre duas posiçoes
def dist_to(pos1, pos2):
    if len(pos1) != 2 or len(pos1) != 2:
        return ''

    x1, y1 = pos1
    x2, y2 = pos2

    return math.sqrt(math.pow((x2-x1), 2) + math.pow((y2-y1), 2))
               

# verifica se duas posicoes estao na msm direcao 
def check_same_direction(pos1, pos2):
    if len(pos1) != 2 or len(pos2) != 2:
        return False

    x1, y1 = pos1
    x2, y2 = pos2

    if x1 == x2 or y1 == y2:
        return True

    return False


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
    if obstaculo == None:
        return False
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

