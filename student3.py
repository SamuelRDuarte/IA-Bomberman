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
        calc_hide_pos = False
        goal = 0,0


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

                
                if state['bombs'] != [] and not calc_hide_pos:
                    print("calcurar hide pos")
                    goal = choose_hide_pos(my_pos,state['bombs'][0],state['enemies'],mapa,[0,0])
                    print('my pos:',my_pos)
                    print(goal)
                    calc_hide_pos = True
                    key = goto(my_pos,goal)
                
                if state['bombs'] != [] and calc_hide_pos:
                    if dist_to(my_pos,goal) != 0:
                        print("ir para hide pos")
                        key = goto(my_pos,goal)

                    else: # esta seguro, espera ate a bomba rebentar
                        print("Esperar que a bomba rebente...")
                        key = ''
                else: # nao ha bombas
                    calc_hide_pos = False
                    if state['walls'] == [] and state['enemies'] != [] and state['powerups'] == []:

                        print("going to kill enemies")
                        if dist_to(my_pos, (1,1)) == 0:
                            key = 'B'
                            ways.append('B')
                        else:
                            goal = 1,1
                            key = goto(my_pos,goal)
                            #key = choose_move(my_pos, ways, [1, 1])

                    # ir para 'exit'
                    if state['walls'] == [] and state['enemies'] == [] and state['powerups'] == []:
                        print("going to exit")
                        goal = state['exit']
                        key = goto(my_pos, goal)

                    # apanhar powerups
                    if state['walls'] == [] and state['powerups'] != []:
                        print("going to powerups")
                        goal = state['powerups'][0][0]
                        key = goto(my_pos,goal )

                    if state['walls'] != []:
                        print("Procurar parede...")
                        goal = next_wall(my_pos, state['walls'])

                        print('dist to wall: ', end='')
                        print(dist_to(my_pos, goal))

                        # por bomba se tiver perto da parede
                        if dist_to(my_pos, goal) <= 1:
                            print('Cheguei à parede! Pôr bomba!')
                            key = 'B'
                            ways.append('B')                           

                        # anda até a parede
                        else:
                            print('Andar até à parede: ' + str(goal))
                            key = goto(my_pos, goal)


                if key != '':
                    if not key in ways:
                        print('Caminho impossivel... escolhendo novo')
                        key = choose_move(my_pos, ways, goal)

                previous_key = key
                print('Sending key: ' + key)

                ##17/10 - Fugir dos inimigos
                ord_enemies = closer_enemies(my_pos, state['enemies'])
                for i in range(len(ord_enemies)):
                    if dist_to(my_pos, ord_enemies[i][1]) < 3:
                        key = avoid(my_pos, ord_enemies[i][1], mapa)
                        break
                        print("FUGI\n")

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