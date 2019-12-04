from defs2 import in_range, get_possible_ways
from enemy import closer_enemies

def choose_hide_pos(bomberman_pos, bomb, mapa, previous_key, n, limit,enemies,detonador):
    x,y = bomberman_pos

    ord_enemies = closer_enemies(bomberman_pos, enemies)
    if detonador:
        raio = 2
    else:
        raio = 4

    if not in_range(bomberman_pos, bomb[2], bomb[0], mapa) and not in_range(bomberman_pos,raio, ord_enemies[0][1], mapa):
        return (bomberman_pos, True)


    if n == limit:
        if bomberman_pos != bomb[0]:
            return (bomberman_pos, False)
        else:
            return (bomb[0], False)

    ways = get_possible_ways(mapa, bomberman_pos)

    if previous_key in ['a', 'd']: # andou para o lado, experimenta para o cima/baixo
        if 'w' in ways and not in_range(mapa.calc_pos(bomberman_pos,'w'),1, ord_enemies[0][1], mapa):
            return choose_hide_pos([x, y - 1], bomb, mapa, 'w', n + 1, limit,enemies,detonador)

        if 's' in ways and not in_range(mapa.calc_pos(bomberman_pos,'s'),1, ord_enemies[0][1], mapa):
            return choose_hide_pos([x,y+1], bomb, mapa, 's', n+1, limit,enemies,detonador)

    if previous_key in ['w', 's']: # andou na vertical, experimenta para os lados
        if 'a' in ways and not in_range(mapa.calc_pos(bomberman_pos, 'a'), 1, ord_enemies[0][1], mapa):
            return choose_hide_pos([x - 1, y], bomb, mapa, 'a', n + 1, limit, enemies, detonador)

        if 'd' in ways and not in_range(mapa.calc_pos(bomberman_pos,'d'),1, ord_enemies[0][1], mapa):
            return choose_hide_pos([x + 1, y], bomb, mapa, 'd', n+1, limit,enemies,detonador)


    if 'w' in ways and not in_range(mapa.calc_pos(bomberman_pos, 'w'), 1, ord_enemies[0][1], mapa):
        return choose_hide_pos([x, y - 1], bomb, mapa, 'w', n + 1, limit, enemies, detonador)

    if 's' in ways and not in_range(mapa.calc_pos(bomberman_pos, 's'), 1, ord_enemies[0][1], mapa):
        return choose_hide_pos([x, y + 1], bomb, mapa, 's', n + 1, limit, enemies, detonador)

    if 'a' in ways and not in_range(mapa.calc_pos(bomberman_pos, 'a'), 1, ord_enemies[0][1], mapa):
        return choose_hide_pos([x - 1, y], bomb, mapa, 'a', n + 1, limit, enemies, detonador)

    if 'd' in ways and not in_range(mapa.calc_pos(bomberman_pos,'d'),1, ord_enemies[0][1], mapa):
        return choose_hide_pos([x + 1, y], bomb, mapa, 'd', n+1, limit,enemies,detonador)
    else:
        return bomberman_pos,False




def choose_hide_pos2(bomberman_pos, bomb, mapa, previous_key, n, limit,enemies,detonador):
    x,y = bomberman_pos

    ord_enemies = closer_enemies(bomberman_pos, enemies)

    if detonador:
        raio = 2
    else:
        raio = 4

    if not in_range(bomberman_pos, bomb[2], bomb[0], mapa)and not in_range(bomberman_pos,raio, ord_enemies[0][1], mapa) :
        return (bomberman_pos, True)

    if n == limit:
        return choose_hide_pos(bomberman_pos,bomb,mapa,'',0,70,enemies,detonador)

    ways = get_possible_ways(mapa, bomberman_pos)

    if previous_key in ['a', 'd']: # andou para o lado, experimenta para o cima/baixo
        if 's' in ways and not in_range(mapa.calc_pos(bomberman_pos,'s'),1, ord_enemies[0][1], mapa):
            return choose_hide_pos2([x,y+1], bomb, mapa, 's', n+1, limit,enemies,detonador)

        if 'w' in ways and not in_range(mapa.calc_pos(bomberman_pos,'w'),1, ord_enemies[0][1], mapa):
            return choose_hide_pos2([x, y - 1], bomb, mapa, 'w', n+1, limit,enemies,detonador)

    if previous_key in ['w', 's']: # andou na vertical, experimenta para os lados
        if 'd' in ways and not in_range(mapa.calc_pos(bomberman_pos, 'd'), 1, ord_enemies[0][1], mapa):
            return choose_hide_pos2([x + 1, y], bomb, mapa, 'd', n + 1, limit, enemies, detonador)
        if 'a' in ways and not in_range(mapa.calc_pos(bomberman_pos,'a'),1, ord_enemies[0][1], mapa):
            return choose_hide_pos2([x-1,y], bomb, mapa, 'a', n+1, limit,enemies,detonador)

    if 's' in ways and not in_range(mapa.calc_pos(bomberman_pos,'s'),1, ord_enemies[0][1], mapa):
        return choose_hide_pos2([x, y + 1], bomb, mapa, 's', n+1, limit,enemies,detonador)

    if 'w' in ways and not in_range(mapa.calc_pos(bomberman_pos,'w'),1, ord_enemies[0][1], mapa):
        return choose_hide_pos2([x, y - 1], bomb, mapa, 'w', n+1, limit,enemies,detonador)

    if 'd' in ways and not in_range(mapa.calc_pos(bomberman_pos, 'd'), 1, ord_enemies[0][1], mapa):
        return choose_hide_pos2([x + 1, y], bomb, mapa, 'd', n + 1, limit, enemies, detonador)

    if 'a' in ways and not in_range(mapa.calc_pos(bomberman_pos,'a'),1, ord_enemies[0][1], mapa):
        return choose_hide_pos2([x-1,y], bomb, mapa, 'a', n+1, limit,enemies,detonador)
    else:
        return choose_hide_pos(bomb[0],bomb,mapa,previous_key,n+1,limit,enemies,detonador)

