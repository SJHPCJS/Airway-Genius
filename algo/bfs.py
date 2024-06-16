from collections import deque

from numpy import random


def BFS(max_fuel: int,
        fuel_cost: int,
        forbidden_area: set[tuple[int, int]],
        carrier_airport_list: list[tuple[int, int]],
        tanker_list: list[tuple[int, int]],
        start_pos: tuple[int, int],
        end_pos: tuple[int, int],
        map_size: tuple[int, int]):
    visited = dict()  # store the visited position and the remaining fuel

    queue = deque([(start_pos, max_fuel, ())])  # store the position, remaining fuel, and the path
    visited.update({start_pos: max_fuel})  # initialize the start position with max fuel

    while queue:
        cur_pos: tuple[int, int]
        cur_fuel: int
        path: tuple
        cur_pos, cur_fuel, path = queue.popleft()
        path = path + (cur_pos,)

        if cur_fuel < 0:
            # skip if the fuel is negative
            continue
        if cur_pos == end_pos:
            # return the path if the destination is reached
            return path

        neighbors = get_neighbors(cur_pos, map_size)
        random.shuffle(neighbors)  # shuffle the neighbors to get random path(visually better)
        for neighbor in neighbors:
            if neighbor in forbidden_area:
                # skip if the neighbor is forbidden
                continue
            is_visited = neighbor in visited
            is_refuel = neighbor in carrier_airport_list or neighbor in tanker_list
            if is_refuel:
                # refuel if the neighbor is a carrier or airport or tanker and update the fuel at the poisition
                queue.append((neighbor, max_fuel, path))
                visited.update({neighbor: max_fuel})
            elif is_visited and cur_fuel - fuel_cost > visited[neighbor] or not is_visited:
                # update the fuel at the position and add the neighbor to the queue
                # if current fuel - fuel cost is greater than the fuel previously visited,
                # it means that can start from the neighbor with more fuel and reach further
                new_fuel = cur_fuel - fuel_cost
                queue.append((neighbor, new_fuel, path))
                visited.update({neighbor: new_fuel})

    # return empty list if no path found
    return []


def get_neighbors(cur_pos, map_size):
    neighbors = []
    x, y = cur_pos
    width, height = map_size
    if x - 1 >= 0:
        neighbors.append((x - 1, y))
    if x + 1 < width:
        neighbors.append((x + 1, y))
    if y - 1 >= 0:
        neighbors.append((x, y - 1))
    if y + 1 < height:
        neighbors.append((x, y + 1))
    return neighbors
