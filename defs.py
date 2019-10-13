from game import Bomb
from mapa import Map

def vector2dir(vx, vy):
    m = max(abs(vx), abs(vy))
    if m == abs(vx):
        if vx < 0:
            d = 'a'  # 'a'
        else:
            d = 'd'  # 'd'
    else:
        if vy > 0:
            d = 's'  # s
        else:
            d = 'w'  # w
    return d


def goto(origem, destino):
    if len(origem) != 2 or len(destino) != 2:
        return ''

    ox, oy = origem
    dx, dy = destino

    return vector2dir(dx - ox, dy - oy)


def foundWall(pos, wall):
    dist1= pos[0] - wall[0]
    dist2= pos[1] - wall[1]

    if dist1>=-1 and dist1<=1:
        return True
    elif dist2>=-1 and dist2<=1:
        return True
    else:
        return False


def go_hide(bombs, bomberman_pos, previous_key):
    if bombs == []:
        return

    bx = bomberman_pos[0]
    by = bomberman_pos[1]

    for bomb in bombs:
        if not bomb.in_range(bomberman_pos):
            return

        # so foge numa direcao
        if previous_key == 'a': # fugir para a direita
            return goto(bomberman_pos, [bx + bomb.radius + 1, by])

        elif previous_key == 'd': # fugir para a esquerda
            return goto(bomberman_pos, [bx - (bomb.radius + 1), by])

        elif previous_key == 'w': # fugir para baixo
            return goto(bomberman_pos, [bx, by + bomb.radius + 1])
            
        elif previous_key == 's': # fugir para cima
            return goto(bomberman_pos, [bx, by - (bomb.radius + 1)])
