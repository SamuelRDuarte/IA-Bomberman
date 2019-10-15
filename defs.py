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

def novapos(pos,mapa):
    x,y = pos
    if not mapa.is_stone((x,y+1)):
        print("BAIXO\n")
        return 's'
    if not mapa.is_stone((x+1,y)):
        print("DIREITA\n")
        return 'd'
    if not mapa.is_stone((x-1,y)):
        print("ESQUERDA\n")
        return 'a'
    if not mapa.is_stone((x,y-1)):
        print("CIMA\n")
        return 'a'

# para qualquer posicao retorna um lista de possoveis movimentos
def get_possible_ways(mapa, position):  
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

# da lista de possiveis caminhos escolhe um caminho random
def choose_random_move(ways):
    if len(ways) == 1:
        return ways[0]

    index = random.randint(0, len(ways)-1)
    print('index: ' + str(index))
    print('random_key: ' + ways[index])
    return ways[index]

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


#def next_wall(walls): 

# ------------------------------------------------------------

def go_hide(bomb, bomberman_pos, previous_key):

    bx = bomberman_pos[0]
    by = bomberman_pos[1]

    #print('raio: ' +  str(bomb[2]))
    raio = bomb[2]

    # so foge numa direcao
    if previous_key == 'a': # fugir para a direita
        return goto(bomberman_pos, [bx + raio + 1, by])

    elif previous_key == 'd': # fugir para a esquerda
        return goto(bomberman_pos, [bx - (raio + 1), by])

    elif previous_key == 'w': # fugir para baixo
        return goto(bomberman_pos, [bx, by + raio + 1])
            
    elif previous_key == 's': # fugir para cima
        return goto(bomberman_pos, [bx, by - (raio + 1)])

    else: print('nao fugi lixei me com f 0')


def in_range(bomb, bomberman_pos, mapa):
    bx, by, raio = bomb
    mx, my = bomberman_pos

    if by == my:
        for r in range(raio + 1):
            if mapa.is_stone((bx + r, by)):
                break  # protected by stone to the right
            if (mx, my) == (bx + r, by):
                return True
        for r in range(raio + 1):
            if mapa.is_stone((bx - r, by)):
                break  # protected by stone to the left 
            if (mx, my) == (bx - r, by):
                return True
    if bx == mx:
        for r in range(raio + 1):
            if mapa.is_stone((bx, by + r)):
                break  # protected by stone in the bottom
            if (mx, my) == (bx, by + r):
                return True
        for r in range(raio + 1):
            if mapa.is_stone((bx, by - r)):
                break  # protected by stone in the top
            if (mx, my) == (bx, by - r):
                return True

    return False
