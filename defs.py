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
def get_possible_ways(mapa, position):  
    ways = []

    x, y = position
    '''print(mapa.map)
    print(position)
    print(mapa.map[x+1][y])
    print(mapa.map[x][y+1])
    print(mapa.map[x-1][y])
    print(mapa.map[x][y-1])'''
    
    if not mapa.is_blocked([x+1, y]):
        
        ways.append('d')
    if not mapa.is_blocked([x, y+1]):
        
        ways.append('s')
    if not mapa.is_blocked([x-1, y]):
        ways.append('a')
        
    if not mapa.is_blocked([x, y-1]):
        
        ways.append('w')

    return ways

def get_possible_ways2(mapa, position):  
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

def choose_move(my_pos, ways, goal):
    if len(ways) == 0:
        return ''

    mx, my = my_pos
    
    custo_min = []

    if 'a' in ways:
        custo_min.append(('a', dist_to([mx-1, my], goal)))        
    if 's' in ways:
        custo_min.append(('s', dist_to([mx, my+1], goal)))
    if 'd' in ways:
        custo_min.append(('d', dist_to([mx+1, my], goal)))
    if 'w' in ways:
        custo_min.append(('w', dist_to([mx, my-1], goal)))


    print('lista antes de ordendar: ' + str(custo_min))
    custo_min.sort(key= lambda x: x[1]) # ordenar por custo (distancia)

    print('lista depois de ordendar: ' + str(custo_min))

    return custo_min[0][0]
               

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



#Verifica o mais perto   ---> A funcionar
def closer_enemies(my_pos,list):
    lista1=[]

    for i in range(len(list)):
        coor=list[i]['pos']
        lista1.append([dist_to(my_pos,list[i]['pos']),list[i]['pos']])

        #Guarda uma lista de tuplos (id e distancia), ordenada por distancias
    lista1.sort(key=lambda x: x[0])  # ordenar por custo (distancia)
    print (lista1)

    return lista1



#evita os inimigos
def avoid(my_pos,en_pos,mapa):
    if en_pos[0]>my_pos[0]:                                             #Inimigo à direita
        if not Map.is_stone(mapa,[my_pos[0]-1,my_pos[1]]):                       #BOmberman vai à esquerda
            print("ESQUERDA")
            return 'a'
        else:                                                           #Pedra à esquerda
            if en_pos[1]>my_pos[1]:                                     #Inimigo acima
                if not Map.is_stone(mapa,[my_pos[0], my_pos[1]-1]):              #Bomberman para baixo
                    print("BAIXO")
                    return 's'
                else:
                    print("rip")
                    return ''

            else:                                                       #Inimigo abaixo
                if not Map.is_stone(mapa,[my_pos[0], my_pos[1]+1]):              #Bomberman para cima
                    print("CIMA")
                    return 'w'
                else:
                    print("rip")
                    return ''

    else:                                                               #Inimigo à esquerda
        if not Map.is_stone(mapa,[my_pos[0] + 1, my_pos[1]]):  # BOmberman vai à direita
            print("DIREITA")
            return 'd'
        else:  # Pedra à direita
            if en_pos[1] > my_pos[1]:  # Inimigo acima
                if not Map.is_stone(mapa,[my_pos[0], my_pos[1] - 1]):  # Bomberman para baixo
                    print("Baixo")
                    return 's'
                else:
                    print("rip")
                    return ''

            else:  # Inimigo abaixo
                if not Map.is_stone(mapa,[my_pos[0], my_pos[1] + 1]):  # Bomberman para cima
                    print("CIMA")
                    return 'w'
                else:
                    print("rip")
                    return ''

