# source: https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
import math

class Node:
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position 

        # f = cost + heuristic
        self.cost = 0
        self.heuristic = 0
        self.f = 0

    def __eq__(self, value):
        return self.position == value.position

    def dist_to(self, pos):
        return math.pow((self.position[0] - pos.position[0]), 2) + math.pow((self.position[1] - pos.position[1]), 2)


def astar(maze, start, end, mapa, exat_pos):
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""

    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)

    # Loop until you find the end
    count_open_nodes = 0
    while len(open_list) > 0:

        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found the goal
        distToGoal = 1

        if exat_pos:
            distToGoal = 0

        if current_node.dist_to(end_node) <= distToGoal:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1] # Return reversed path

        # Generate children
        children = []
        count = 0
                            # tirei as diagonais
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # Adjacent squares

            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze[len(maze)-1]) -1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            if node_position in mapa.walls or mapa.is_stone(node_position):
            #if maze.getTile(node_position):
                continue

            # Create new node
            new_node = Node(current_node, node_position)
            count += 1

            if count > 4:
                return []

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:

            # Child is on the closed list
            if child in closed_list:
                continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
            #child.h = math.sqrt((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
            child.f = child.g + child.h

            # Child is already in the open list
            for open_node in open_list:
                if child == open_node and child.g > open_node.g:
                    continue

            # Add the child to the open list
            open_list.append(child)
            count_open_nodes += 1
            if count_open_nodes > 300:
                return []





