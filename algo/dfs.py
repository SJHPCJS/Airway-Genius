from numpy import random
import sys

global local_max_fuel
global local_fuel_cost
global local_forbidden_area_coords_list
global local_carrier_airport_list
global local_tanker_list
global local_start_pos
global local_end_pos
global local_map_size
global best_distance
global shortest_path_coords_list
global visited
global local_forbidden_area
global path_coords_list


def get_neighbors(cur_pos):
    """
    get the neighbors of the current position
    :param cur_pos: the current position
    :return: the neighbors list
    """
    neighbors = []
    x, y = cur_pos[0], cur_pos[1]
    width, height = local_map_size[0], local_map_size[1]
    if x - 1 >= 0:
        neighbors.append((x - 1, y))
    if x + 1 < width:
        neighbors.append((x + 1, y))
    if y - 1 >= 0:
        neighbors.append((x, y - 1))
    if y + 1 < height:
        neighbors.append((x, y + 1))
    return neighbors


def DFS(max_fuel: int,
        fuel_cost: int,
        forbidden_area: set[tuple[int, int]],
        carrier_airport_list: list[tuple[int, int]],
        tanker_list: list[tuple[int, int]],
        start_pos: tuple[int, int],
        end_pos: tuple[int, int],
        map_size: tuple[int, int]):
    global best_distance
    global shortest_path_coords_list
    global local_max_fuel
    global local_fuel_cost
    global local_carrier_airport_list
    global local_tanker_list
    global local_start_pos
    global local_end_pos
    global local_map_size
    global visited
    global local_forbidden_area
    global path_coords_list
    local_max_fuel = max_fuel
    local_carrier_airport_list = carrier_airport_list
    local_tanker_list = tanker_list
    local_start_pos = start_pos
    local_end_pos = end_pos
    local_fuel_cost = fuel_cost
    local_map_size = map_size
    best_distance = local_map_size[0] * local_map_size[1]
    shortest_path_coords_list = None
    local_forbidden_area = forbidden_area
    path_coords_list = []
    visited = dict()
    # set the maximum recursion depth
    sys.setrecursionlimit(2500)
    DFS_auxiliary(max_fuel, start_pos, 0)
    print("DFS finished")
    print(best_distance)
    return shortest_path_coords_list if shortest_path_coords_list is not None else []


def DFS_auxiliary(cur_fuel: int, cur_pos: tuple[int, int], cur_distance: int):
    global best_distance
    global shortest_path_coords_list
    global local_max_fuel
    global local_fuel_cost
    global local_forbidden_area_coords_list
    global local_carrier_airport_list
    global local_tanker_list
    global local_start_pos
    global local_end_pos
    global local_map_size
    global visited
    global local_forbidden_area
    global path_coords_list
    path_coords_list.append(cur_pos)
    if cur_fuel < 0:
        return
    if cur_distance >= best_distance:
        return
    if cur_pos[0] == local_end_pos[0] and cur_pos[1] == local_end_pos[1]:
        if cur_distance < best_distance:
            best_distance = cur_distance
            shortest_path_coords_list = path_coords_list.copy()
        return
    if cur_fuel == 0:
        return
    visited.update({cur_pos: cur_fuel})
    neighbors = get_neighbors(cur_pos)
    if random.randint(0, 20) == 0:
        random.shuffle(neighbors)
    for neighbor in neighbors:
    # for neighbor in get_neighbors(cur_pos):
        if neighbor in local_forbidden_area:
            continue
        is_refuel = neighbor in local_carrier_airport_list or neighbor in local_tanker_list
        is_visited = neighbor in visited
        if is_refuel and not is_visited:
            DFS_auxiliary(local_max_fuel, neighbor, cur_distance + 1)
            path_coords_list.pop()
        elif is_visited and cur_fuel - local_fuel_cost > visited[neighbor] or not is_visited:
            new_fuel = cur_fuel - local_fuel_cost
            DFS_auxiliary(new_fuel, neighbor, cur_distance + 1)
            path_coords_list.pop()
    return
