from Node import *
from mapa import Map
import random
from defs2 import dist_to

def getKey(pos):
    if len(pos) != 2:
        return ''
    
    if pos == [1,0]:
        return 'd'
    elif pos == [-1,0]:
        return 'a'
    elif pos == [0,1]:
        return 's'
    elif pos == [0,-1]:
        return 'w' 
    else:
        return ''

def goToPosition(my_pos, next_pos):

    mx,my = my_pos
    nx,ny = next_pos

    res = [nx-mx, ny-my]
    return getKey(res)


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

    custo_min.sort(key= lambda x: x[1]) # ordenar por custo (distancia)

    return custo_min[0][0]


def choose_key(mapa, ways, my_pos, positions, goal, last_pos_wanted):
    # já sabe o caminho
    if positions != []:
        while my_pos == positions[0]:
            positions.pop(0)

        key = goToPosition(my_pos, positions[0])
        positions.pop(0)
        return key, positions

    else: # pesquisar caminho
        positions = astar(mapa.map, my_pos, goal, mapa, last_pos_wanted)

        if positions == [] or positions == None:
            return choose_move(my_pos, ways, goal), []

        if len(positions) > 1:
            positions.pop(0)

        return goToPosition(my_pos, positions[0]),positions


# retorna a key para um inimigo ou '' caso nao encontre
def pathToEnemy(mapa, my_pos, enemy_pos):
    # procura caminho para inimigo
    if enemy_pos is not None:
        # procura caminho para o inimigo
        positions = astar(mapa.map, my_pos, enemy_pos, mapa, False)

        if positions != [] and positions is not None:
            if len(positions) == 1:
                return 'B'

            # se a posiçao seguinte for igual à posiçao atual
            # tira essa posição da lista
            while dist_to(my_pos, positions[0]) == 0:
                positions.pop(0)

            return goToPosition(my_pos, positions[0])

        # nao encontrou caminho
        return ''

# pesquisa caminho para objetivo
def findPath(mapa, my_pos, goal, exact_pos):
    positions = astar(mapa.map, my_pos, goal, mapa, exact_pos)

    # nao encontra caminho para o objetivo
    if positions == [] or positions == None:
        return []

    # se a proxima posiçao for igual à minha posiçao atual
    while dist_to(my_pos, positions[0]) == 0:
        positions.pop(0)

    return positions

    

# retorna a key para uma parede
def keyPath(my_pos, positions):
    # nao precisa de pesquisar caminho
    if positions != []:
        key = goToPosition(my_pos, positions[0])
        goal = positions[-1]
        positions.pop(0)
        return key, positions, goal


def goTo(mapa, my_pos, ways, positions, goal, exact_pos):
    # nao sabe o caminho -> pesquisa
    if positions == []:
        path = findPath(mapa, my_pos, goal, exact_pos)

        # nao foi possivel encontrar caminho -> usa outra função
        if path == []:
            key = choose_move(my_pos, ways, goal)
            return key, [], goal
        
        positions = path

    # ja tem caminho
    return keyPath(my_pos, positions)