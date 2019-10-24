import sys
import json
import asyncio
import websockets
import getpass
import os

from defs import *
from mapa import Map


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

                my_pos = state['bomberman']
                ways = get_possible_ways(mapa, my_pos)

                print('ways: ', end='')
                print(ways)
                '''
                # se houver bombas foge
                if state['bombs'] != []:
                    pos_bomb, t, raio = state['bombs'][0]

                    sameDir = check_same_direction(pos_bomb, my_pos)
                    print('Same direction?: ' + str(sameDir))


                    if dist_to(my_pos, pos_bomb) <= raio:
                        if sameDir:
                            print('Fugirrr')
                            if dist_to(my_pos, pos_bomb) >= 1:
                                direcao_proibida = inverse(previous_key)
                                print('Proibido: ' + str(direcao_proibida))
                                if direcao_proibida in ways:
                                    ways.remove(direcao_proibida)
                                key = choose_random_move(ways)

                            else:
                                key = choose_random_move(ways)

                        else: # esta seguro, espera ate a bomba rebentar
                            print("Esperar que a bomba rebente...")
                            key = ''
                    else: # esta seguro, espera ate a bomba rebentar
                        print("Esperar que a bomba rebente...")
                        key = ''

                    '''
                # fuga recursiva
                if state['bombs'] != [] and not calc_hide_pos:
                    print("calcurar hide pos")
                    goal, calc_hide_pos = choose_hide_pos2(my_pos, state['bombs'][0], mapa, '', 0, 100)
                    print('my pos:', my_pos)
                    print(goal)
                    print('hide pos: ' + str(calc_hide_pos))
                    key = choose_move(my_pos, ways, goal)
                    print('key hide pos in cacl:', key)

                if state['bombs'] != [] and calc_hide_pos:
                    print('já sabe a hide pos!')
                    if dist_to(my_pos, goal) != 0:
                        print("ir para hide pos")
                        key = choose_move(my_pos, ways, goal)
                        print('key hide pos :', key)

                    else:  # esta seguro, espera ate a bomba rebentar
                        print("Esperar que a bomba rebente...")
                        key = ''

                elif state['bombs'] == []:  # nao ha bombas
                    calc_hide_pos = False

                    if state['walls'] == [] and state['enemies'] != [] and state['powerups'] == []:

                        print("going to kill enemies")
                        if dist_to(my_pos, (1, 1)) == 0:
                            key = 'B'
                            ways.append('B')
                        else:
                            # key = goto(my_pos,(1,1))
                            key = choose_move(my_pos, ways, [1, 1])

                    # ir para 'exit'
                    if state['walls'] == [] and state['enemies'] == [] and state['powerups'] == []:
                        print("going to exit")
                        key = choose_move(my_pos, ways, state['exit'])

                    # apanhar powerups
                    if state['powerups'] != []:
                        print("going to powerups")
                        key = choose_move(my_pos, ways, state['powerups'][0][0])

                    if state['walls'] != [] and state['powerups'] == []:
                        print("Procurar parede...")
                        wall = next_wall(my_pos, state['walls'])

                        print('dist to wall: ', end='')
                        print(dist_to(my_pos, wall))

                        # por bomba se tiver perto da parede
                        if dist_to(my_pos, wall) <= 1:
                            print('Cheguei à parede! Pôr bomba!')
                            key = 'B'
                            ways.append('B')

                            # anda até a parede
                        else:
                            print('Andar até à parede: ' + str(wall))
                            key = goto(my_pos, wall)

                ##17/10 - Fugir dos inimigos
                if state['enemies'] != [] and state['bombs'] == []:
                    ord_enemies = closer_enemies(my_pos, state['enemies'])
                    if dist_to(my_pos, ord_enemies[0][1]) < 2:
                        key = avoid(my_pos, ord_enemies[0][1], mapa)
                        # print("FUGI\n")

                if key != '' or key == None:
                    if not key in ways:
                        print('Caminho impossivel... escolhendo novo')
                        key = choose_move(my_pos, ways, wall)

                previous_key = key
                print('Sending key: ' + key + '\n\n')

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
