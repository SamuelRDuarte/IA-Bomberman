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

        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game state, this must be called timely or your game will get out of sync with the server
                # Next lines are only for the Human Agent, the key values are nonetheless the correct ones!
                key = ""

                print(state)
                # atualizar mapa
                mapa._walls = state['walls']

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


                my_pos = state['bomberman']
                ways = get_possible_ways(mapa, my_pos)
                if my_pos == powerup:
                    got_powerup = True
                    if state['level'] == 3:
                        detonador = True

                print('ways: ', end='')
                print(ways)

                # fuga recursiva
                if state['bombs'] != [] and not calc_hide_pos:
                    print("calcurar hide pos")
                    goal, calc_hide_pos = choose_hide_pos2(my_pos, state['bombs'][0], mapa, '', 0, 60, state['enemies'])
                    print('my pos:', my_pos)
                    print(goal)
                    print('hide pos: ' + str(calc_hide_pos))
                    key = choose_move(my_pos, ways, goal)
                    # key = choose_key(mapa, my_pos, positions, goal, True)
                    print('key hide pos in cacl:', key)

                elif state['bombs'] != [] and calc_hide_pos:
                    print('já sabe a hide pos!')
                    if dist_to(my_pos, goal) != 0:
                        print("ir para hide pos")
                        key = choose_move(my_pos, ways, goal)
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

                elif state['bombs'] == []:  # nao ha bombas
                    calc_hide_pos = False
                    oneils = [e for e in state['enemies'] if e['name'] == 'Oneal']

                    if state['walls'] == [] and state['enemies'] != [] and state['powerups'] == []:

                        print("going to kill enemies")
                        if dist_to(my_pos, (1, 1)) == 0:
                            key = 'B'
                            ways.append('B')
                        else:
                            # key = goto(my_pos,(1,1))
                            # key = choose_move(my_pos, ways, [1, 1])
                            key,positions = choose_key(mapa, ways, my_pos, positions, [1, 1], True)
                            goal = [1,1]

                    # apanhar powerups
                    elif state['powerups'] != []:
                        print("going to powerups")
                        # key = choose_move(my_pos,ways,state['powerups'][0][0])
                        key,positions = choose_key(mapa, ways, my_pos, positions, state['powerups'][0][0], True)
                        goal = state['powerups'][0][0]
                        powerup = state['powerups'][0][0]


                    # ir para 'exit'
                    elif got_powerup and state['enemies'] == [] and state['exit'] != []:
                        print("going to exit")
                        key,positions = choose_key(mapa, ways, my_pos, positions, state['exit'], True)
                        goal = state['exit']
                        # key = choose_move(my_pos,ways,state['exit'])
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
                            if in_range(my_pos, 1, oneils[0]['pos'], mapa):
                                print('Enemie close! Pôr bomba!')
                                key = 'B'
                                ways.append('B')
                        # anda até a parede
                            else:
                                print('Encontrar caminho até à parede alvo: ' + str(wall))
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

                    if in_range(my_pos, 3, ballooms[0]['pos'], mapa):
                        print('Enemie close! Pôr bomba!')
                        key = 'B'
                        ways.append('B')

               # garantir que key é válida
                if key != '' or key == None:
                    if not key in ways:
                        print('Caminho impossivel... escolhendo novo')
                        key = choose_move(my_pos, ways, goal)

                history.append(my_pos)
                previous_level = state['level']
                previous_lives = state['lives']
                previous_key = key
                print('Sending key: ' + key + '\n\n')
                print("got_powerup: ",got_powerup)
                print('Detonador: ', detonador)

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
