from defs2 import dist_to, in_range

def enemie_close(bomberman_pos,enimies,mapa):
    for eni in enimies:
        if in_range(bomberman_pos,1,eni['pos'],mapa):
            return True
    return False


#Verifica o mais perto   ---> A funcionar
def closer_enemies(my_pos,lista):
    lista1=[]
    if lista == []:
        return [(None,None)]

    for i in range(len(lista)):
        coor=lista[i]['pos']
        lista1.append([dist_to(my_pos,lista[i]['pos']),lista[i]['pos']])

        #Guarda uma lista de tuplos (id e distancia), ordenada por distancias
    lista1.sort(key=lambda x: x[0])  # ordenar por custo (distancia)

    return lista1


def predict_dir(lista_pos):
    if lista_pos[-1] == lista_pos[-2]:
        x1,y1 = lista_pos[-1]
        x2, y2 = lista_pos[-2]
        x3, y3= lista_pos[-3]
        if x1 > x2:
            return "d"
        elif x1<x2:
            return "a"
        elif y1>y2:
            return "s"
        elif y1<y2:
            return "w"
        else:
            return ""
