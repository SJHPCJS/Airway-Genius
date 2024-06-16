import heapq
from typing import Optional


# Heuristic function for A* algorithm
def heuristic_cost(pos1: tuple[int, int], pos2: tuple[int, int]):
    return abs(pos2[0] - pos1[0]) + abs(pos2[1] - pos1[1])


# To check if a point is in the range of map size
def border_check(node: tuple[int, int], map_size: tuple[int, int]):
    return (0 <= node[0] < map_size[0]) and (0 <= node[1] < map_size[1])

# To get neighbors of a point in the range of map size
def neighbors(node: tuple[int, int], map_size: tuple[int, int]):
    neighbor_list = []

    if border_check((node[0], node[1] - 1), map_size):
        neighbor_list.append((node[0], node[1] - 1))
    if border_check((node[0], node[1] + 1), map_size):
        neighbor_list.append((node[0], node[1] + 1))
    if border_check((node[0] - 1, node[1]), map_size):
        neighbor_list.append((node[0] - 1, node[1]))
    if border_check((node[0] + 1, node[1]), map_size):
        neighbor_list.append((node[0] + 1, node[1]))

    return neighbor_list


# main A* algorithm
def get_astar_path(came_from: dict[tuple[int, int], Optional[tuple[int, int]]], end_pos: tuple[int, int]):
    if came_from.get(end_pos) is None:
        return []
    else:
        path = []
        reverse_pos = end_pos
        while reverse_pos is not None:
            path.append(reverse_pos)
            reverse_pos = came_from.get(reverse_pos)
        return list(reversed(path))


def astar(max_fuel: int,
          fuel_cost: int,
          forbidden_area_coords_set: set[tuple[int, int]],
          carrier_airport_list: list[tuple[int, int]],
          tanker_list: list[tuple[int, int]],
          start_pos: tuple[int, int],
          end_pos: tuple[int, int],
          map_size: tuple[int, int]):

    # initialize aux data
    add_fuel_pos_set = set(carrier_airport_list + tanker_list)

    came_from: dict[tuple[int, int], Optional[tuple[int, int]]] = {}
    cost_so_far: dict[tuple[int, int], int] = {}
    fuel_so_far: dict[tuple[int, int], int] = {}
    path: tuple

    came_from[start_pos] = None
    cost_so_far[start_pos] = 0
    fuel_so_far[start_pos] = max_fuel
    frontier = [(0, start_pos, max_fuel, ())]

    # main loop to find path
    while frontier:
        current = heapq.heappop(frontier)
        path = current[3]
        path = path + (current[1],)

        # find path
        if current[1] == end_pos:
            return list(path)
            # break

        # cost and fuel calculation logic
        for next_node in neighbors(current[1], map_size):
            if next_node in forbidden_area_coords_set:
                continue

            new_cost = cost_so_far[current[1]] + 1
            if next_node in add_fuel_pos_set:
                new_fuel = max_fuel
            else:
                new_fuel = current[2] - fuel_cost

            if new_fuel < 0:
                continue

            # update aux data
            if next_node not in cost_so_far or new_fuel > fuel_so_far[next_node]:
                cost_so_far[next_node] = new_cost
                fuel_so_far[next_node] = new_fuel
                new_priority = new_cost + heuristic_cost(next_node, end_pos)
                heapq.heappush(frontier, (new_priority, next_node, new_fuel, path))
                came_from[next_node] = current[1]

    # if not found
    return []

