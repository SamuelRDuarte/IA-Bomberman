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


def closeToWall(pos, wall):             # verificar a distancia ate uma parede (pode estar atras de uma parede indestrutivel pelo meio)
    if len(pos) != 2 or len(wall) != 2:
        return False

    px, py = pos
    wx, wy = wall

