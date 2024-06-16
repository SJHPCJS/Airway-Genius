
import heapq
import random


class Node:
    def __init__(self, node_type=0):
        self.node_type = node_type
        self.visited = 0

    def __str__(self):
        return f"({self.node_type}, {self.visited})"

    __repr__ = __str__

def init_map(map_size, forbidden=None, carrier_airport=None, tanker=None):
    if forbidden is None:
        forbidden = []
    if carrier_airport is None:
        carrier_airport = []
    if tanker is None:
        tanker = []

    map_grid = []
    forbidden_set = set(forbidden)
    carrier_set = set(carrier_airport)
    tanker_set = set(tanker)

    for i in range(map_size[0]):
        row = []
        for j in range(map_size[1]):
            node_type = 0
            if (i, j) in forbidden_set:
                visited = 1
            else:
                visited = 0
                if (i, j) in carrier_set:
                    node_type = 1
                elif (i, j) in tanker_set:
                    node_type = 2
            node = Node(node_type)
            node.visited = visited
            row.append(node)
        map_grid.append(row)
    return map_grid


def dijkstra_first_search(map_grid, start_pos, end_pos, fuel_cost, max_fuel):
    size = len(map_grid)
    distances = {(i, j): float('inf') for i in range(len(map_grid)) for j in range(len(map_grid[0]))}
    distances[start_pos] = 0
    previous_nodes = {start_pos: None}
    # store the distance, position, and fuel remaining
    priority_queue = [(0, start_pos, max_fuel)]
    fuel_used = {(i, j): float('inf') for i in range(len(map_grid)) for j in range(len(map_grid[0]))}
    # initialize the fuel used at the start position to 0
    fuel_used[start_pos] = 0
    # 4 directions: north, south, east, west
    direction = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while priority_queue:

        current_distance, (current_x, current_y), current_fuel = heapq.heappop(priority_queue)

        if map_grid[current_x][current_y].visited == 1:
            continue

        if current_fuel <= 0:
            continue

        if map_grid[current_x][current_y].node_type in [1, 2]:
            current_fuel = max_fuel

        if (current_x, current_y) == end_pos:
            break


        neighbors = [(current_x - 1, current_y), (current_x + 1, current_y), (current_x, current_y - 1),
                     (current_x, current_y + 1)]

        for (nx, ny) in neighbors:
            if 0 <= nx < len(map_grid) and 0 <= ny < len(map_grid[0]) and map_grid[nx][ny].visited == 0:
                if map_grid[nx][ny].node_type in [1, 2]:
                    distance = current_distance + 1  # no random weight for refueling stations
                else:
                    distance = current_distance + 1
                if distance < distances[(nx, ny)] or distance == distances[(nx, ny)] and current_fuel - fuel_cost > fuel_used[(nx, ny)]:
                    distances[(nx, ny)] = distance
                    fuel_needed = current_fuel - fuel_cost
                    if fuel_needed >= 0:
                        fuel_used[(nx, ny)] = fuel_needed
                        previous_nodes[(nx, ny)] = (current_x, current_y)
                        heapq.heappush(priority_queue, (distance, (nx, ny), fuel_needed))
    # if the distance at the end position is infinity, return empty lists
    if distances[end_pos] == float('infinity'):
        return [], []

    path = []
    current_node = end_pos
    while current_node is not None:
        path.append(current_node)
        current_node = previous_nodes[current_node]
    path.reverse()

    # Find all refueling stations in the path
    refueling_stations = [node for node in path if map_grid[node[0]][node[1]].node_type in [1, 2]]

    print("Dijkstra 1st finished" "path lenth: ", len(path))
    return path, refueling_stations

def dijkstra_second_search(map_grid, start_pos, end_pos, fuel_cost, max_fuel):
    size = len(map_grid)
    distances = {(i, j): float('inf') for i in range(len(map_grid)) for j in range(len(map_grid[0]))}
    distances[start_pos] = 0
    previous_nodes = {start_pos: None}
    # store the distance, position, and fuel remaining
    priority_queue = [(0, start_pos, max_fuel)]
    fuel_used = {(i, j): float('inf') for i in range(len(map_grid)) for j in range(len(map_grid[0]))}
    # initialize the fuel used at the start position to 0
    fuel_used[start_pos] = 0
    # 4 directions: north, south, east, west
    direction = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while priority_queue:

        current_distance, (current_x, current_y), current_fuel = heapq.heappop(priority_queue)

        if map_grid[current_x][current_y].visited == 1:
            continue

        if current_fuel <= 0:
            continue

        if map_grid[current_x][current_y].node_type in [1, 2]:
            current_fuel = max_fuel

        if (current_x, current_y) == end_pos:
            break

        neighbors = [(current_x - 1, current_y), (current_x + 1, current_y), (current_x, current_y - 1),
                     (current_x, current_y + 1)]
        for (nx, ny) in neighbors:
            if 0 <= nx < len(map_grid) and 0 <= ny < len(map_grid[0]) and map_grid[nx][ny].visited == 0:
                if map_grid[nx][ny].node_type in [1, 2]:
                    distance = current_distance + 1  # no random weight for refueling stations
                else:
                    distance = current_distance + 1 + random.uniform(0, 0.00000000001)
                if distance < distances[(nx, ny)] or distance == distances[(nx, ny)] and current_fuel - fuel_cost > fuel_used[(nx, ny)]:
                    distances[(nx, ny)] = distance
                    fuel_needed = current_fuel - fuel_cost
                    if fuel_needed >= 0:
                        fuel_used[(nx, ny)] = fuel_needed
                        previous_nodes[(nx, ny)] = (current_x, current_y)
                        heapq.heappush(priority_queue, (distance, (nx, ny), fuel_needed))

    if distances[end_pos] == float('infinity'):
        return []

    path = []
    current_node = end_pos
    while current_node is not None:
        path.append(current_node)
        current_node = previous_nodes[current_node]
    path.reverse()

    print("Dijkstra 2st finished" "path lenth: ", len(path))
    return path

# Advanced Dijkstra Search Algorithm (with refueling stations)
def advanced_dijkstra_search(map_grid, start_pos, end_pos, fuel_cost, max_fuel):
    # First search to find the path and refueling stations
    first_path, refueling_stations = dijkstra_first_search(map_grid, start_pos, end_pos, fuel_cost, max_fuel)
    if not first_path:
        return []

    # Second search to find the final path
    final_path = [start_pos]

    # Iterate through the refueling stations
    for i in range(len(refueling_stations)):
        if i == 0:
            prev_station = start_pos
        else:
            prev_station = refueling_stations[i - 1]
        current_station = refueling_stations[i]
        # Path segment from the previous refueling station to the current refueling station
        path_segment = dijkstra_second_search(map_grid, prev_station, current_station, fuel_cost, max_fuel)
        final_path += path_segment[1:]
    # Last path segment from the last refueling station to the end position
    last_path_segment = dijkstra_second_search(map_grid, refueling_stations[-1], end_pos, fuel_cost, max_fuel)
    final_path += last_path_segment[1:]

    return final_path
