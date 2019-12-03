import sys
import json
import asyncio
import websockets
import getpass
import os

from defs2 import *
from mapa import Map
from Node import *
from path import *
from bomb import *


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
        previos_pos = None
        samePosCounter = 0
        positions = []
        history = []
        limite = 0
        got_powerup = False
        powerup = [0,0]
        detonador = False
        wallpass = False
        bombpass = False
        change=False
        enemyCloseCounter = 0
        goal = []
        samePosBomba = 0
        corner = None

        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game state, this must be called timely or your game will get out of sync with the server
                # Next lines are only for the Human Agent, the key values are nonetheless the correct ones!

                if state['level'] == 15 and state['enemies'] == []:
                    return 0

                if state['lives'] == 0:
                    return 0

                key = ""

                print(state)
                # atualizar mapa
                mapa.walls = state['walls']

                level = state['level']

                if previous_level != None and previous_lives != None:
                    # se morrer ou passar de nível faz reset às variáveis globais
                    if previous_level != state['level']:
                        got_powerup = False
                        powerup = [0,0]
                        previos_pos = None
                        samePosCounter = 0

                    if previous_level != state['level'] or previous_lives != state['lives']:
                        print('RESET')
                        calc_hide_pos = False
                        previous_level = state['level']
                        previous_lives = state['lives']
                        positions = []
                        history = []
                        goal = []
                        enemyCloseCounter = 0

                
                if corner == None:
                    corner = find_corner(mapa)

                # ignora powerups não utilizados
                if level == 2 or level == 5 or level == 6 or level == 10 or level == 11 or level == 12 or level == 13 or level == 14 or level==15:
                    got_powerup = True

                if detonador:
                    if level == 8 or level == 13:
                        got_powerup = True


                my_pos = state['bomberman']
                ways = get_possible_ways(mapa, my_pos)
                print('ways: ', end='')
                print(ways)

                # verificar se tem detonador
                if my_pos == powerup:
                    got_powerup = True
                    if level == 3 or level == 8 or level == 13:
                        detonador = True
                    if level == 9:
                        bombpass = True

                    
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
                    change = False

                elif state['bombs'] != [] and calc_hide_pos:
                    print('já sabe a hide pos!')

                    if detonador:
                        if samePosBomba >=3:
                            change = True
                        if my_pos == previos_pos:
                            samePosBomba += 1
                        else:
                            samePosBomba = 0

                    print('change: ' , change)

                    '''
                    if len(history) > 11:
                        for i in range(0,10):
                            if history[i] != history[i+1]:
                                change= False
                    '''

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
                        change = False
                        goal, calc_hide_pos = choose_hide_pos2(my_pos, state['bombs'][0], mapa, '', 0, 60, state['enemies'],detonador)
                        print('nova hide pos: ',goal)
                        key=choose_move(my_pos,ways,goal)

                elif state['bombs'] == []:  # nao ha bombas
                    calc_hide_pos = False
                    # enquanto nao tiver detonador nao procura ballons
                    if detonador == True:
                        enemies = state['enemies']
                    else:
                        enemies = [e for e in state['enemies'] if e['name'] in ['Oneal','Minvo','Kondoria','Ovapi','Pass']]

                    enemies = state['enemies']

                    # só há inimigos vai atras deles
                    if state['walls'] == [] and state['enemies'] != [] and state['powerups'] == []:

                        enemies = [e for e in state['enemies'] if e['name'] in ['Oneal','Minvo','Kondoria','Ovapi','Pass']]
                        
                        if enemies !=[]:
                            enemies.sort(key=lambda x: dist_to(my_pos, x['pos']))

                            distToClosestEnemy = dist_to(my_pos, enemies[0]['pos'])
                            print('DisToClosestEnemy: ' + str(distToClosestEnemy))
                            print('enemy_pos: ' + str(enemies[0]['pos']))
                            key = pathToEnemy(mapa, my_pos, enemies[0]['pos'])
                            goal = enemies[0]['pos']

                            # se tiver perto do inimigo incrementa o contador
                            if distToClosestEnemy < 2.5:
                                print('Perto do inimigo!')
                                enemyCloseCounter += 1

                            elif enemyCloseCounter > 20:
                                print('Ciclo infinito encontrado!!!'.center(50, '-'))
                                # vai para uma parede
                                #print('Encontrar caminho até à parede alvo: ' + str(wall))
                                goal = list(mapa.bomberman_spawn)
                                key = choose_move(my_pos,ways,goal)
                                enemyCloseCounter = 0
                                print('goal: ',goal)

                            
                        elif dist_to(my_pos, corner) == 0:
                            print("going to kill enemies")
                            enemies = state['enemies']
                            enemies.sort(key=lambda x: dist_to(my_pos, x['pos']))
                            if dist_to(list(corner), enemies[0]['pos']) < 6:
                                key = 'B'
                                ways.append('B')
                            else:
                                pass
                        else:
                            key, positions = choose_key(mapa, ways, my_pos, positions, list(corner), True)
                            goal = list(corner)
                        

                    # apanhar powerups
                    elif state['powerups'] != []:
                        print("going to powerups")
                        #key = choose_move(my_pos,ways,state['powerups'][0][0])
                        #key,positions = choose_key(mapa, ways, my_pos, positions, state['powerups'][0][0], True)
                        powerup = state['powerups'][0][0]

                        key, positions, goal = goTo(mapa, my_pos, ways, positions, powerup, True)
                        print('positions: ' + str(positions))
                        print('key from goTo (powerup): ' + key)
                        print('goal' + str(goal))
                        if state['walls']:
                            parede = min(state['walls'], key=lambda x: dist_to(my_pos, x))
                            if dist_to(my_pos, parede) <= 1:
                                key = 'B'
                                ways.append('B')


                    # ir para 'exit'
                    elif got_powerup and state['enemies'] == [] and state['exit'] != []:
                        print("going to exit")

                        key, positions, goal = goTo(mapa, my_pos, ways, positions, state['exit'], True)
                        if key == '':
                            key, positions, goal = goTo(mapa, my_pos, ways, positions, state['exit'], True)
                        print('positions: ' + str(positions))
                        print('key from goTo (exit): ' + key)
                        print('goal' + str(goal))

                        if state['walls']:
                            parede = min(state['walls'], key=lambda x: dist_to(my_pos, x))
                            if dist_to(my_pos, parede) <= 1:
                                key = 'B'
                                ways.append('B')

                    # ha paredes            
                    elif state['walls'] != []:
                        print("Escolher parede alvo...")
                        print('my' + str(my_pos))


                        '''if positions == [] or positions is None:
                            print("Escolher nova parede: ")'''
                        wall = next_wall(my_pos, state['walls'])
                        print('parede: ', wall)

                        print('dist to wall: ', end='')
                        print(dist_to(my_pos, wall))

                        if len(enemies) == 1 and not got_powerup: #para apanhar o powerup
                            enemies = []


                        # por bomba se tiver perto da parede
                        if dist_to(my_pos, wall) <= 1:
                            print('Cheguei à parede! Pôr bomba!')
                            key = 'B'
                            ways.append('B')


                        # ha inimigos
                        elif enemies !=[] :
                            enemies.sort(key=lambda x: dist_to(my_pos, x['pos']))

                            distToClosestEnemy = dist_to(my_pos, enemies[0]['pos'])
                            print('DisToClosestEnemy: ' + str(distToClosestEnemy))
                            
                            # se tiver perto do inimigo incrementa o contador
                            if distToClosestEnemy < 2.5:
                                print('Perto do inimigo!')
                                enemyCloseCounter += 1


                            # verificar ciclo com inimigo
                            if enemyCloseCounter > 20:
                                print('Ciclo infinito com inimigo encontrado!!!'.center(50, '-'))
                                # vai destruir parede mais proxima
                                key, positions, goal = goTo(mapa, my_pos, ways, positions, wall, False)
                                print('Encontrar caminho até à parede alvo: ' + str(wall))
                                enemyCloseCounter = 0
                                print('positions: ' + str(positions))
                                print('key from ciclo enimie: ' + key)
                                print('goal: ',goal)

                            # procura caminho para inimigo e parede
                            else:
                                # procura caminho para inimigo
                                key = pathToEnemy(mapa, my_pos, enemies[0]['pos'])

                                if key == '':
                                    key, positions, goal = goTo(mapa, my_pos, ways, positions, wall,False)
                                    print('positions: ' + str(positions))
                                    print('key from gotoWall: ' + key)
                                    print('goal' + str(goal))


                        else:
                            print('Encontrar caminho até à parede alvo: ' + str(wall))
                            key, positions, goal = goTo(mapa, my_pos, ways, positions, wall,False)
                            print('positions: ' + str(positions))
                            print('key from gotoWall: ' + key)
                            print('goal' + str(goal))


                if state['enemies'] != [] and state['bombs'] == []:
                    ##17/10 - Fugir dos inimigos
                    enemies = state['enemies']
                    enemies.sort(key=lambda x: dist_to(my_pos, x['pos']))
                    if key in ['w','s','d','a']:
                        if in_range(mapa.calc_pos(my_pos,key), 1, enemies[0]['pos'], mapa):
                            print('Enemie close! Pôr bomba! (Calculado)')
                            key = 'B'
                            ways.append('B')
                    if in_range(my_pos, 1, enemies[0]['pos'], mapa):
                        print('Enemie close! Pôr bomba!')
                        key = 'B'
                        ways.append('B')


                if my_pos == previos_pos:
                    samePosCounter += 1
                    if samePosCounter >= 20:
                        print('Suicidio'.center(80, '/'))
                        if state['bombs'] != []:
                            if detonador:
                                key = 'A'
                                ways.append('A')
                        else:
                            key = choose_random_move(ways)
                            print ('key random:'+ key)
                            samePosCounter = 0
                else:
                    print('Reset samePosCounter!')
                    samePosCounter = 0

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
                previos_pos = my_pos
                print('Sending key: ' + key + '\n\n')
                print("got_powerup: ",got_powerup)
                print('Detonador: ', detonador)
                print('Bombpass: ', bombpass)
                print('corner: ', str(corner))

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
