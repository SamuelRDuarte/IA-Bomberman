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
        history=[]

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
                    if previous_level != state['level'] or previous_lives != state['lives']:
                        print('RESET')
                        calc_hide_pos = False
                        previous_level = state['level']
                        previous_lives = state['lives']
                        positions = []
                        history=[]
                
                
                my_pos = state['bomberman']
                ways = get_possible_ways(mapa, my_pos)


                print('ways: ', end='')
                print(ways)

                # fuga recursiva
                if state['bombs'] != [] and not calc_hide_pos:
                    print("calcurar hide pos")
                    goal, calc_hide_pos = choose_hide_pos2(my_pos, state['bombs'][0], mapa, '', 0, 70, state['enemies'])
                    print('my pos:',my_pos)
                    print(goal)
                    print('hide pos: ' + str(calc_hide_pos))
                    key = choose_move(my_pos, ways, goal)
                    #key = choose_key(mapa, my_pos, positions, goal, True)
                    print('key hide pos in cacl:',key)
                
                if state['bombs'] != [] and calc_hide_pos:
                    print('já sabe a hide pos!')
                    if dist_to(my_pos, goal) != 0:
                        print("ir para hide pos")
                        key = choose_move(my_pos, ways, goal)
                        #key = choose_key(mapa, my_pos, positions, goal, True)
                        print('key hide pos :',key)

                    else: # esta seguro, espera ate a bomba rebentar
                        print("Esperar que a bomba rebente...")
                        key = ''

                elif state['bombs'] == []: # nao ha bombas
                    calc_hide_pos = False

                    if state['walls'] == [] and state['enemies'] != [] and state['powerups'] == []:

                        print("going to kill enemies")
                        if dist_to(my_pos, (1,1)) == 0:
                            key = 'B'
                            ways.append('B')
                        else:
                            #key = goto(my_pos,(1,1))
                            #key = choose_move(my_pos, ways, [1, 1])
                            key = choose_key(mapa, ways, my_pos, positions, [1,1], True)

                    # ir para 'exit'
                    if state['walls'] == [] and state['enemies'] == [] and state['powerups'] == []:
                        print("going to exit")
                        key = choose_key(mapa, ways, my_pos, positions, state['exit'], True)
                        #key = choose_move(my_pos,ways,state['exit'])

                    # apanhar powerups
                    if state['powerups'] != []:
                        print("going to powerups")
                        #key = choose_move(my_pos,ways,state['powerups'][0][0])
                        key = choose_key(mapa, ways, my_pos, positions, state['powerups'][0][0], True)


                    if state['walls'] != [] and state['powerups'] == []:
                        print("Escolher parede alvo...")
                        print('my' + str(my_pos))

                        if positions == []:
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
                            print('Encontrar caminho até à parede alvo: ' + str(wall))
                            key = choose_key(mapa, ways, my_pos, positions, wall, False)




                    oneils = [e for e in state['enemies'] if e['name'] == 'Oneal']

                    if oneils != [] :
                        oneils.sort(key=lambda x: dist_to(my_pos, x['pos']))

                        if in_range(my_pos, 1, oneils[0]['pos'], mapa):
                            print('Enemie close! Pôr bomba!')
                            key = 'B'
                            ways.append('B')


                        if oneils != [] and dist_to(my_pos,oneils[0]['pos'])>1:
                            key = choose_key(mapa, ways, my_pos, positions, oneils[0]['pos'], False)

                    if len(history)>=2:
                        if history[len(history)-1] == history[len(history)-2]:
                            key=choose_random_move(ways)
                            print ("\n\n\nTINHA BUGADO\n\n\n")


                if state['enemies'] !=[] and state['bombs'] ==[]:
                    ##17/10 - Fugir dos inimigos
                    ballooms = []
                    ballooms = [b for b in state['enemies'] if b['name'] == "Balloom"]
                    ballooms.sort(key=lambda x: dist_to(my_pos, x['pos']))

                    if in_range(my_pos,3, ballooms[0]['pos'], mapa):
                        print('Enemie close! Pôr bomba!')
                        key = 'B'
                        ways.append('B')

                ''' 
                # garantir que key é válida
                if key != '' or key == None:
                    if not key in ways:
                        print('Caminho impossivel... escolhendo novo')
                        key = choose_move(my_pos, ways, wall)
                '''
                
                history.append(my_pos)
                previous_level = state['level']
                previous_lives = state['lives']
                previous_key = key
                print('Sending key: ' + key + '\n\n')

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
