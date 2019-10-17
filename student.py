import sys
import json
import asyncio
import websockets
import getpass
import os

from defs import *
from mapa import Map

def novapos(pos,mapa):
    x,y = pos
    if not mapa.is_stone((x,y+1)):
        print("BAIXO\n")
        return 's'
    if not mapa.is_stone((x+1,y)):
        print("DIREITA\n")
        return 'd'
    if not mapa.is_stone((x-1,y)):
        print("ESQUERDA\n")
        return 'a'
    if not mapa.is_stone((x,y-1)):
        print("CIMA\n")
        return 'a'




async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))
        msg = await websocket.recv()
        game_properties = json.loads(msg)

        # You can create your own map representation or use the game representation:
        mapa = Map(size=game_properties["size"], mapa=game_properties["map"])

        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game state, this must be called timely or your game will get out of sync with the server                
                # Next lines are only for the Human Agent, the key values are nonetheless the correct ones!
                key = ""
                
                print(state)

                first_wall = state['walls'][0]                
                my_pos = state['bomberman']

                if not foundWall(my_pos,first_wall):
                    next_step = goto(my_pos, first_wall)
                else:
                    next_step= goto(my_pos,[30,30])   #coordenadas à toa

                print(next_step)

                new_pos = mapa.calc_pos(my_pos,next_step)

                if my_pos != new_pos:
                    key = next_step
                else:
                    key = novapos(my_pos,mapa)


                await websocket.send(
                    json.dumps({"cmd": "key", "key": key})
                )  # send key command to server - you must implement this send in the AI agent
                #break
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return




  ##17/10 - Fugir dos inimigos
                        if state['enemies'] != []:
                            ord_enemies = closer_enemies(my_pos, state['enemies'])
                            for i in range(len(ord_enemies)):
                                if dist_to(my_pos, ord_enemies[i][1]) < 10:
                                    key = avoid(my_pos, ord_enemies[i][1], mapa)
                                    break
                                    print("FUGI\n")



#Verifica o mais perto   ---> A funcionar
def closer_enemies(my_pos,list):
    lista1=[]

    for i in range(len(list)):
        coor=list[i]['pos']
        lista1.append([dist_to(my_pos,list[i]['pos']),list[i]['pos']])

        #Guarda uma lista de tuplos (id e distancia), ordenada por distancias
    bubble_sort(lista1)

    return lista1



#evita os inimigos
def avoid(my_pos,en_pos,mapa):
    if en_pos[0]>my_pos[0]:                                             #Inimigo à direita
        if not Map.is_stone(mapa,[my_pos[0]-1,my_pos[1]]):                       #BOmberman vai à esquerda
            print("ESQUERDA")
            return 'a'
        else:                                                           #Pedra à esquerda
            if en_pos[1]>my_pos[1]:                                     #Inimigo acima
                if not Map.is_stone(mapa,[my_pos[0], my_pos[1]-1]):              #Bomberman para baixo
                    print("BAIXO")
                    return 's'
                else:
                    print("rip")
                    return ''

            else:                                                       #Inimigo abaixo
                if not Map.is_stone(mapa,[my_pos[0], my_pos[1]+1]):              #Bomberman para cima
                    print("CIMA")
                    return 'w'
                else:
                    print("rip")
                    return ''

    else:                                                               #Inimigo à esquerda
        if not Map.is_stone(mapa,[my_pos[0] + 1, my_pos[1]]):  # BOmberman vai à direita
            print("DIREITA")
            return 'd'
        else:  # Pedra à direita
            if en_pos[1] > my_pos[1]:  # Inimigo acima
                if not Map.is_stone(mapa,[my_pos[0], my_pos[1] - 1]):  # Bomberman para baixo
                    print("Baixo")
                    return 's'
                else:
                    print("rip")
                    return ''

            else:  # Inimigo abaixo
                if not Map.is_stone(mapa,[my_pos[0], my_pos[1] + 1]):  # Bomberman para cima
                    print("CIMA")
                    return 'w'
                else:
                    print("rip")
                    return ''






# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='bombastico' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
