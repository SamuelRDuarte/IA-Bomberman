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

        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game state, this must be called timely or your game will get out of sync with the server
                # Next lines are only for the Human Agent, the key values are nonetheless the correct ones!
                key = ""

                # atualizar mapa
                mapa._walls = state['walls']

                level = state['level']

                if previous_level != None and previous_lives != None:
                    # se morrer ou passar de nível faz reset às variáveis globais
                    if previous_level != state['level']:
                        got_powerup = False
                        powerup = [0,0]
                        previos_pos = None
                        samePosCounter = 0

                    if previous_level != state['level'] or previous_lives != state['lives']:
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

                # verificar se tem detonador
                if my_pos == powerup:
                    got_powerup = True
                    if level == 3:
                        detonador = True
                    if level == 9:
                        bombpass = True
                    if level == 10:
                        wallpass = True

                    
                # fuga recursiva
                if state['bombs'] != [] and not calc_hide_pos:
                    goal, calc_hide_pos = choose_hide_pos2(my_pos, state['bombs'][0], mapa, '', 0, 60, state['enemies'],detonador)
                    key = choose_move(my_pos, ways, goal)
                    # key = choose_key(mapa, my_pos, positions, goal, True)
                    change = False

                elif state['bombs'] != [] and calc_hide_pos:

                    if detonador:
                        if history[0] == history[1] and history[0] == history[2]:
                            change = True
                   

                    if not change:
                        if dist_to(my_pos, goal) != 0:
                            key = choose_move(my_pos, ways, goal)
                            # key = choose_key(mapa, my_pos, positions, goal, True)

                        else:  # esta seguro, espera ate a bomba rebentar
                            if detonador:
                                key = 'A'
                                ways.append('A')
                            else:                                
                                key = ''

                    else:
                        change = False
                        goal, calc_hide_pos = choose_hide_pos2(my_pos, state['bombs'][0], mapa, '', 0, 60, state['enemies'],detonador)
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
                            key = choose_move(my_pos,ways,oneils[0]['pos'])
                            # se tiver perto do inimigo incrementa o contador
                            if distToClosestEnemy < 2.5:                              
                                enemyCloseCounter += 1

                            elif enemyCloseCounter > 20:
                                # vai para uma parede
                                #print('Encontrar caminho até à parede alvo: ' + str(wall))
                                goal = [1,1]
                                key = choose_move(my_pos,ways,goal)
                                enemyCloseCounter = 0

                            

                        elif dist_to(my_pos, (1, 1)) == 0:
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


                        if positions == []:
                            wall = next_wall(my_pos, state['walls'])

                        # por bomba se tiver perto da parede
                        if dist_to(my_pos, wall) <= 1:
                            key = 'B'
                            ways.append('B')
                        #para apanhar o detonator
                        elif state['level'] == 3 and len(oneils) == 1 and not detonador:
                            key,positions= choose_key(mapa, ways, my_pos, positions, wall, False)
                            goal = wall

                        elif oneils !=[]:
                            oneils.sort(key=lambda x: dist_to(my_pos, x['pos']))

                            distToClosestEnemy = dist_to(my_pos, oneils[0]['pos'])
                            
                            # se tiver perto do inimigo incrementa o contador
                            if distToClosestEnemy < 2.5:
                                enemyCloseCounter += 1

                            # nunca entra neste if
                            if in_range(my_pos, 0, oneils[0]['pos'], mapa):
                                key = 'B'
                                ways.append('B')

                            # verificar ciclo com inimigo
                            elif enemyCloseCounter > 20:
                                # vai para uma parede
                                key,positions= choose_key(mapa, ways, my_pos, positions, wall, False)
                                goal = wall
                                enemyCloseCounter = 0

                            # procura caminho para inimigo e parede
                            else:
                                key,goal = choose_key2(mapa, ways, my_pos, positions, wall,oneils[0]['pos'], False)


                        else:
                            key,positions= choose_key(mapa, ways, my_pos, positions, wall, False)
                            goal = wall

                if state['enemies'] != [] and state['bombs'] == []:
                    ##17/10 - Fugir dos inimigos
                    ballooms = state['enemies']
                    ballooms.sort(key=lambda x: dist_to(my_pos, x['pos']))
                    if key in ['w','s','d','a']:
                        if in_range(mapa.calc_pos(my_pos,key), 1, ballooms[0]['pos'], mapa):
                            key = 'B'
                            ways.append('B')
                    else:
                        if in_range(my_pos, 1, ballooms[0]['pos'], mapa):
                            key = 'B'
                            ways.append('B')

                if my_pos == previos_pos:
                    samePosCounter += 1
                    if samePosCounter >= 250:
                        if state['bombs'] != []:
                            if detonador:
                                key = 'A'
                                ways.append('A')
                        else:
                            key = 'B'
                            ways.append('B')
                            samePosCounter = 0
                else:
                    samePosCounter = 0

               # garantir que key é válida
                if key != '' or key == None:
                    if not key in ways:
                        if goal:
                            key = choose_move(my_pos, ways, goal)
                        else:
                            key = choose_move(my_pos,ways,next_wall(my_pos,state['walls']))

                history.append(my_pos)
                previous_level = state['level']
                previous_lives = state['lives']
                previous_key = key
                previos_pos = my_pos
                

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
