from mapa import Map
from path import choose_move, choose_random_move, dist_to, goToPosition
from Node import astar

def choose_key2(mapa, ways, my_pos, positions, wall, oneal, last_pos_wanted):
    # já sabe o caminho

    if positions != []:
        key = goToPosition(my_pos, positions[0])
        positions.pop(0)
        if positions:
            return key,positions[-1]
        else:
            return key,[]

    else:  # pesquisar caminho
        if oneal is not None:
            positions = astar(mapa.map, my_pos, oneal)
            print('positions enemie: ' + str(positions))
            if positions == [] or positions == None:
                positions = astar(mapa.map, my_pos, wall)
                print('positions wall: ' + str(positions))
                if positions == [] or positions == None:
                    print('Caminho nao encontrado...')
                    # return choose_move(my_pos,ways,goal)
                    return choose_random_move(ways),''
                goal = wall
            goal = oneal
        else:
            positions = astar(mapa.map, my_pos, wall)
            print('positions wall: ' + str(positions))
            if positions == [] or positions == None:
                print('Caminho nao encontrado...')
                # return choose_move(my_pos,ways,goal)
                return '', ''
            goal = wall
        if len(positions)>1:
            positions.pop(0)

        if len(positions) <= 1 and last_pos_wanted:
            return choose_move(my_pos, ways, goal),goal

        return goToPosition(my_pos, positions[0]),goal


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




#evita os inimigos
def avoid(my_pos,en_pos,mapa):

    # if en_pos[0] == my_pos[0]:
    #     if not Map.is_blocked(mapa, [my_pos[0], my_pos[1] - 1]):  # Bomberman para baixo
    #         print("BAIXO")
    #         return 's'
    #     else:
    #         print("CIMA")
    #         return 'w'
    #
    # elif en_pos[1]==mu


    if en_pos[0]>my_pos[0]:                                             #Inimigo à direita
        if not Map.is_blocked(mapa,[my_pos[0]-1,my_pos[1]]):                       #BOmberman vai à esquerda
            print("ESQUERDA")
            return 'a'
        else:                                                           #Pedra à esquerda
            if en_pos[1]>my_pos[1]:                                     #Inimigo abaixo
                if not Map.is_blocked(mapa,[my_pos[0], my_pos[1]-1]):              #Bomberman para cima
                    print("CIMA")
                    return 'w'
            elif en_pos[1] < my_pos[1]:  # Inimigo acima
                if not Map.is_blocked(mapa, [my_pos[0], my_pos[1] + 1]):  # Bomberman para baixo
                    print("BAIXO")
                    return 's'
                else:
                    print("rip")

            else:                                                       # INIMIGO NO MESMO NIVEL
                if not Map.is_blocked(mapa, [my_pos[0], my_pos[1] - 1]):  # Bomberman para cima
                    print("CIMA")
                    return 'w'
                else:
                    print("BAIXO")
                    return 's'


    elif en_pos[0]<my_pos[0]:                                                               #Inimigo à esquerda
        if not Map.is_blocked(mapa,[my_pos[0] + 1, my_pos[1]]):  # BOmberman vai à direita
            print("DIREITA")
            return 'd'
        else:                                                   # Pedra à direita
            if en_pos[1] > my_pos[1]:  # Inimigo abaixo
                if not Map.is_blocked(mapa,[my_pos[0], my_pos[1] - 1]):  # Bomberman para cima
                    print("CIMA")
                    return 'w'
                else:
                    print("rip")
                    return ''

            elif en_pos[1] < my_pos[1]:
                if not Map.is_blocked(mapa,[my_pos[0], my_pos[1] + 1]):  # Bomberman para baixo
                    print("BAIXO")
                    return 's'
                else:
                    print("rip")
                    return ''


            else:  # Inimigo NO MESMO NIVEL
                if not Map.is_blocked(mapa,[my_pos[0], my_pos[1] - 1]):  # Bomberman para cima
                    print("CIMA")
                    return 'w'
                else:
                    print("BAIXO")
                    return 's'


    else:                                                               #INIMIGO EM LINHA
        if en_pos[1] > my_pos[1]:  # Inimigo acima
            if not Map.is_blocked(mapa, [my_pos[0], my_pos[1] - 1]):  # Bomberman para cima
                print("CIMA")
                return 'w'
            else:
                print("rip")
                return ''

        elif en_pos[1] < my_pos[1]:
            if not Map.is_blocked(mapa, [my_pos[0], my_pos[1] +  1]):  # Bomberman para baixo
                print("BAIXO")
                return 's'
            else:
                print("rip")
                return ''


        else:  # Inimigo NO MESMO NIVEL
            if not Map.is_blocked(mapa, [my_pos[0], my_pos[1] - 1]):  # Bomberman para cima
                print("CIMA")
                return 'w'
            else:
                print("BAIXO")
                return 's'


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