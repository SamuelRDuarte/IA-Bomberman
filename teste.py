import sys
import json
import asyncio
import websockets
import getpass
import os

from defs import *
from mapa import Map
from Node import *


async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        msg = await websocket.recv()
        game_properties = json.loads(msg)

        # You can create your own map representation or use the game representation:
        mapa = Map(size=game_properties["size"], mapa=game_properties["map"])
        previous_key = ""

        calc_hide_pos = False
        previous_level = None
        previous_lives = None
        positions = []
        history = []
        limite = 0
        got_powerup = False
        powerup = [0,0]
        detonador = False
        wallpass = False
        bombpass = False
        change=True
        enemyCloseCounter = 0
        goal = []

        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game state, this must be called timely or your game will get out of sync with the server
                # Next lines are only for the Human Agent, the key values are nonetheless the correct ones!
                key = ""

                print(state)
                # atualizar mapa
                if state['walls']:
                    mapa._walls = state['walls']

                level = state['level']

                if previous_level != None and previous_lives != None:
                    # se morrer ou passar de nível faz reset às variáveis globais
                    if previous_level != state['level']:
                        got_powerup = False
                        powerup = [0,0]

                    if previous_level != state['level'] or previous_lives != state['lives']:
                        print('RESET')
                        calc_hide_pos = False
                        previous_level = state['level']
                        previous_lives = state['lives']
                        positions = []
                        history = []
                        goal = []
                        enemyCloseCounter = 0

                # ignora powerups não utilizados
                if level == 2 or level == 5 or level == 6 or level == 11 or level == 12 or level == 13 or level == 14:
                    got_powerup = True


                my_pos = state['bomberman']
                ways = get_possible_ways(mapa, my_pos)
                print('ways: ', end='')
                print(ways)

                # verificar se tem detonador
                if my_pos == powerup:
                    got_powerup = True
                    if level == 3:
                        detonador = True
                    if level == 9:
                        bombpass = True
                    if level == 10:
                        wallpass = True

                    
                '''
                #verificar se tem bombpass
                if my_pos == powerup:
                    got_powerup = True
                    

                # verificar se tem wallpass
                if my_pos == powerup:
                    got_powerup = True'''
                    
                # fuga recursiva
                if state['bombs'] != [] and not calc_hide_pos:
                    print("calcurar hide pos")
                    goal, calc_hide_pos = choose_hide_pos2(my_pos, state['bombs'][0], mapa, '', 0, 60, state['enemies'],detonador)
                    print('my pos:', my_pos)
                    print('hide pos calculado:',goal)
                    print('hide pos: ' + str(calc_hide_pos))
                    key = choose_move(my_pos, ways, goal)
                    # key = choose_key(mapa, my_pos, positions, goal, True)
                    print('key hide pos in cacl:', key)

                elif state['bombs'] != [] and calc_hide_pos:
                    print('já sabe a hide pos!')

                    if len(history) > 11:
                        for i in range(0,10):
                            if history[i] != history[i+1]:
                                change= False

                    if not change:
                        if dist_to(my_pos, goal) != 0:
                            print("ir para hide pos")
                            key = choose_move(my_pos, ways, goal)
                            print('hide pos: ', goal)
                            # key = choose_key(mapa, my_pos, positions, goal, True)
                            print('key hide pos :', key)

                        else:  # esta seguro, espera ate a bomba rebentar
                            if detonador:
                                print('Usar detonador')
                                key = 'A'
                                ways.append('A')
                            else:
                                print("Esperar que a bomba rebente...")
                                key = ''

                    else:
                        print("A ir para o [1,1]! ZWA")
                        change=True
                        goal, calc_hide_pos = choose_hide_pos2(my_pos, state['bombs'][0], mapa, '', 0, 60, state['enemies'],detonador)
                        print('nova hide pos: ',goal)
                        key=choose_move(my_pos,ways,goal)

                elif state['bombs'] == []:  # nao ha bombas
                    calc_hide_pos = False
                    # enquanto nao tiver detonador nao procura ballons
                    if detonador == True:
                        oneils = state['enemies']
                    else:
                        oneils = [e for e in state['enemies'] if e['name'] in ['Oneal','Minvo','Kondoria','Ovapi','Pass']]

                    # só há inimigos vai para a posição [1,1]
                    if state['walls'] == [] and state['enemies'] != [] and state['powerups'] == []:

                        oneils = [e for e in state['enemies'] if e['name'] in ['Oneal','Minvo','Kondoria','Ovapi','Pass']]
                        if oneils !=[]:
                            oneils.sort(key=lambda x: dist_to(my_pos, x['pos']))

                            distToClosestEnemy = dist_to(my_pos, oneils[0]['pos'])
                            print('DisToClosestEnemy: ' + str(distToClosestEnemy))
                            key = choose_move(my_pos,ways,oneils[0]['pos'])
                            # se tiver perto do inimigo incrementa o contador
                            if distToClosestEnemy < 2.5:
                                print('Perto do inimigo!')
                                enemyCloseCounter += 1

                            elif enemyCloseCounter > 20:
                                print('Ciclo infinito encontrado!!!'.center(50, '-'))
                                # vai para uma parede
                                #print('Encontrar caminho até à parede alvo: ' + str(wall))
                                goal = [1,1]
                                key = choose_move(my_pos,ways,goal)
                                enemyCloseCounter = 0
                                print('goal: ',goal)

                            

                        elif dist_to(my_pos, (1, 1)) == 0:
                            print("going to kill enemies")
                            ballooms = state['enemies']
                            ballooms.sort(key=lambda x: dist_to(my_pos, x['pos']))
                            if dist_to([1,1],ballooms[0]['pos']) < 6:
                                key = 'B'
                                ways.append('B')
                            else:
                                pass
                        else:
                            # key = goto(my_pos,(1,1))
                            # key = choose_move(my_pos, ways, [1, 1])
                            key,positions = choose_key(mapa, ways, my_pos, positions, [1, 1], True)
                            goal = [1,1]

                    # apanhar powerups
                    elif state['powerups'] != []:
                        print("going to powerups")
                        #key = choose_move(my_pos,ways,state['powerups'][0][0])
                        #key,positions = choose_key(mapa, ways, my_pos, positions, state['powerups'][0][0], True)
                        key = goto(my_pos,state['powerups'][0][0])
                        goal = state['powerups'][0][0]
                        powerup = state['powerups'][0][0]
                        if state['walls']:
                            parede = min(state['walls'], key=lambda x: dist_to(my_pos, x))
                            if dist_to(my_pos, parede) <= 1:
                                key = 'B'
                                ways.append('B')


                    # ir para 'exit'
                    elif got_powerup and state['enemies'] == [] and state['exit'] != []:
                        print("going to exit")
                        #key,positions = choose_key(mapa, ways, my_pos, positions, state['exit'], True)
                        goal = state['exit']
                        key = choose_move(my_pos,ways,state['exit'])
                        if state['walls']:
                            parede = min(state['walls'], key=lambda x: dist_to(my_pos, x))
                            if dist_to(my_pos, parede) <= 1:
                                key = 'B'
                                ways.append('B')

                    # ha paredes            
                    elif state['walls'] != []:
                        print("Escolher parede alvo...")
                        print('my' + str(my_pos))


                        if positions == []:
                            wall = next_wall(my_pos, state['walls'])
                        print('parede: ', wall)


                        print('dist to wall: ', end='')
                        print(dist_to(my_pos, wall))

                        # por bomba se tiver perto da parede
                        if dist_to(my_pos, wall) <= 1:
                            print('Cheguei à parede! Pôr bomba!')
                            key = 'B'
                            ways.append('B')

                        elif oneils !=[]:
                            oneils.sort(key=lambda x: dist_to(my_pos, x['pos']))

                            distToClosestEnemy = dist_to(my_pos, oneils[0]['pos'])
                            print('DisToClosestEnemy: ' + str(distToClosestEnemy))
                            
                            # se tiver perto do inimigo incrementa o contador
                            if distToClosestEnemy < 2.5:
                                print('Perto do inimigo!')
                                enemyCloseCounter += 1

                            # nunca entra neste if
                            if in_range(my_pos, 0, oneils[0]['pos'], mapa):
                                print('Enemie close! Pôr bomba! oneleas')
                                key = 'B'
                                ways.append('B')

                            # verificar ciclo com inimigo
                            elif enemyCloseCounter > 20:
                                print('Ciclo infinito encontrado!!!'.center(50, '-'))
                                # vai para uma parede
                                print('Encontrar caminho até à parede alvo: ' + str(wall))
                                key,positions= choose_key(mapa, ways, my_pos, positions, wall, False)
                                goal = wall
                                enemyCloseCounter = 0
                                print('goal: ',goal)

                            # procura caminho para inimigo e parede
                            else:
                                print('Encontrar caminho até à parede alvo: ' + str(oneils[0]['pos']) +', ' + str(wall))
                                key,goal = choose_key2(mapa, ways, my_pos, positions, wall,oneils[0]['pos'], False)


                        else:
                            print('Encontrar caminho até à parede alvo: ' + str(wall))
                            key,positions= choose_key(mapa, ways, my_pos, positions, wall, False)
                            goal = wall
                            

                    '''if len(history)>=2:
                        if my_pos == history[-1]:
                            if limite == 3:
                                key=choose_random_move(ways)
                                print ("\n\n\nTINHA BUGADO\n\n\n")
                                limite = 0;
                            limite +=1
                        else:
                            limite = 0'''

                if state['enemies'] != [] and state['bombs'] == []:
                    ##17/10 - Fugir dos inimigos
                    ballooms = state['enemies']
                    ballooms.sort(key=lambda x: dist_to(my_pos, x['pos']))
                    if key in ['w','s','d','a']:
                        if in_range(mapa.calc_pos(my_pos,key), 1, ballooms[0]['pos'], mapa):
                            print('Enemie close! Pôr bomba! (Calculado)')
                            key = 'B'
                            ways.append('B')
                    else:
                        if in_range(my_pos, 1, ballooms[0]['pos'], mapa):
                            print('Enemie close! Pôr bomba!')
                            key = 'B'
                            ways.append('B')

               # garantir que key é válida
                if key != '' or key == None:
                    if not key in ways:
                        print('Caminho impossivel... escolhendo novo')
                        print('goal: ',goal)  #quando vai matar inimigos e entra em ciclo infinito o goal que passa é [], não sei porque
                        if goal:
                            key = choose_move(my_pos, ways, goal)
                        else:
                            key = choose_move(my_pos,ways,next_wall(my_pos,state['walls']))

                history.append(my_pos)
                previous_level = state['level']
                previous_lives = state['lives']
                previous_key = key
                print('Sending key: ' + key + '\n\n')
                print("got_powerup: ",got_powerup)
                print('Detonador: ', detonador)
                print('Bombpass: ', bombpass)
                print('Wallpass: ', wallpass)

                await websocket.send(
                    json.dumps({"cmd": "key", "key": key})
                )  # send key command to server - you must implement this send in the AI agent
                # break
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return


# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='bombastico' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))



#choose key para os enemies 
#positions ==[]
#choose key para os enemies

def choose_key2(mapa, ways, my_pos, positions,wall, oneal, last_pos_wanted):
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
                positions = astar(mapa.map,my_pos,wall)
                print('positions wall: ' + str(positions))
                if positions == [] or positions == None:
                    print('Caminho nao encontrado...')
                    # return choose_move(my_pos,ways,goal)
                    return choose_move(my_pos,ways,wall),''
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