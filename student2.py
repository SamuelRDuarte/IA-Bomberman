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

        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game state, this must be called timely or your game will get out of sync with the server                
                # Next lines are only for the Human Agent, the key values are nonetheless the correct ones!
                key = ""
                
                print(state)
                
                my_pos = state['bomberman']

                ways = get_possible_ways(mapa, my_pos)
                print('ways: ', end='')
                print(ways)

                # se houver bombas foge
                if state['bombs'] != []:
                    pos_bomb, t, raio = state['bombs'][0]

                    sameDir = check_same_direction(pos_bomb, my_pos)
                    print('Same direction?: ' + str(sameDir))

                    # so verifica se nao esta na msm direcao que a bomba
                    # falta: verificar se esta fora do raio e nao fugir de onde veio
                    if dist_to(my_pos, pos_bomb) <= raio:
                        if sameDir:
                            print('Fugirrr')
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

                else: # nao ha bombas, ve se ta perto de uma parede para por bomba
                    print("Procurar parede...")
                    first_wall = state['walls'][0]

                    print('dist to wall: ', end='')
                    print(dist_to(my_pos, first_wall))

                    if dist_to(my_pos, first_wall) <= 1:
                        print('Cheguei à parede!')
                        key = 'B'
                        ways.append('B')

                    else:
                        key = goto(my_pos, first_wall)

                if key != '':
                    if not key in ways:
                        key = choose_random_move(ways)

                previous_key = key
                print('Sending key: ' + key)

                await websocket.send(
                    json.dumps({"cmd": "key", "key": key})
                )  # send key command to server - you must implement this send in the AI agent
                #break
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
