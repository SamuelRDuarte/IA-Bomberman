from Node import *
from mapa import Map
from defs2 import dist_to, choose_move

def choose_key3(mapa, ways, my_pos, positions, wall, oneal, last_pos_wanted):
    # já sabe o caminho

    if positions != []:
        print('Não precisa de pesquisar...')
        print('positions: ' + str(positions))

        if dist_to(my_pos, positions[0]) > 1:
            print("Next_pos invalida!!")
            return choose_move(my_pos, ways, wall), [], wall

        key = goToPosition(my_pos, positions[0])
        goal = positions[-1]
        positions.pop(0)
        return key, positions, goal
        '''
        if positions:
            return key, positions, positions[-1]
        else:
            return key, [], positions[-1]
        '''

    else:  # pesquisar caminho
        # procura caminho para inimigo
        if oneal is not None:
            # procura caminho para o inimigo
            positions = astar(mapa.map, my_pos, oneal, mapa)
            print('positions enemie: ' + str(positions))

            # se nao encontra caminho para o inimigo
            # então procura caminho para a parede
            if positions == [] or positions == None:
                print('Caminho nao encontrado para o inimigo...')
                positions = astar(mapa.map, my_pos, wall, mapa)
                print('positions wall: ' + str(positions))

                # nao encontra caminho para a parede
                if positions == [] or positions == None:
                    print('Caminho nao encontrado para a parede...')
                    # usa outra função para encontrar caminho
                    return choose_move(my_pos, ways, wall), [], wall

                # caminho para parede

                # se a proxima posiçao for igual à minha posiçao atual
                while dist_to(my_pos, positions[0]) == 0:
                    print('my_pos == next_pos')
                    print('apagar posições inuteis')
                    positions.pop(0)

                # positions.pop(0)                # *Problemas*
                return goToPosition(my_pos,positions[0]), positions, positions[-1]
            
            else:
                # caminho para inimigo
                # se a proxima posiçao for igual à minha posiçao atual
                while dist_to(my_pos, positions[0]) == 0:
                    print('my_pos == next_pos')
                    print('apagar posições inuteis')
                    positions.pop(0)

                # positions.pop(0)
                return goToPosition(my_pos, positions[0]), positions, positions[-1]
        

        else: # procura caminho para parede (ja nao ha inimigos)
            positions = astar(mapa.map, my_pos, wall)
            print('positions wall: ' + str(positions))
            
            if positions == [] or positions == None:
                print('Caminho nao encontrado...')
                # return choose_move(my_pos,ways,goal)
                return choose_move(my_pos,ways,wall), [], wall
        
        if len(positions)>1:
            positions.pop(0)

        if len(positions) <= 1 and last_pos_wanted:
            return choose_move(my_pos, ways, wall), positions, wall

        return goToPosition(my_pos, positions[0]), positions, wall

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
    print('goToPosition'.center(50, '-'))
    print('my_pos: ' + str(my_pos))
    print('next_pos: ' + str(next_pos))

    mx,my = my_pos
    nx,ny = next_pos

    res = [nx-mx, ny-my]
    print('res: ' + str(res))
    return getKey(res)


# retorna a key para um inimigo ou '' caso nao encontre
def pathToEnemy(mapa, my_pos, enemy_pos):
    # procura caminho para inimigo
    if enemy_pos is not None:
        # procura caminho para o inimigo
        positions = astar(mapa.map, my_pos, enemy_pos, mapa)
        print('positions to enemie: ' + str(positions))

        if positions != [] and positions is not None:
            if len(positions) == 1:
                return 'B'

            # se a posiçao seguinte for igual à posiçao atual
            # tira essa posição da lista
            while dist_to(my_pos, positions[0]) == 0:
                print('my_pos == next_pos')
                print('apagar posições inuteis')
                print('positions' + str(positions))
                positions.pop(0)

            return goToPosition(my_pos, positions[0])

        # nao encontrou caminho
        return ''

# pesquisa caminho para parede
def findPathToWall(mapa, my_pos, wall):
    print('Pesquisando caminho para parede...')
    positions = astar(mapa.map, my_pos, wall, mapa)
    print('positions wall: ' + str(positions))

    # nao encontra caminho para a parede
    if positions == [] or positions == None:
        print('Caminho nao encontrado para a parede...')
        return []

    # se a proxima posiçao for igual à minha posiçao atual
    while dist_to(my_pos, positions[0]) == 0:
        print('my_pos == next_pos')
        print('apagar posições inuteis')
        positions.pop(0)

    # impossivel seguir caminho -> pesquisa outra vez
    if dist_to(my_pos, positions[0]) > 1:
        print("Next_pos invalida!! - Pesquisar caminho outra vez!!")

    return positions

    

# retorna a key para uma parede
def keyPathToWall(my_pos, positions):
    # nao precisa de pesquisar caminho
    if positions != []:
        print('Não precisa de pesquisar...')
        print('positions: ' + str(positions))

        key = goToPosition(my_pos, positions[0])
        goal = positions[-1]
        positions.pop(0)
        return key, positions, goal
        



def goToWall(mapa, my_pos, ways, positions, wall):
    # nao sabe o caminho -> pesquisa
    if positions == []:
        path = findPathToWall(mapa, my_pos, wall)

        # nao foi possivel encontrar caminho -> usa outra função
        if path == []:
            key = choose_move(my_pos, ways, wall)
            return key, [], wall
        
        positions = path

    # ja tem caminho
    return keyPathToWall(my_pos, positions)