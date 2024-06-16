import time

from airway_genius_gui.globals import AlgoType
from algo.advanced_dijkstra import advanced_dijkstra_search, init_map as advanced_dijkstra_init_map
from algo.astar import astar
from algo.bfs import BFS
from algo.dfs import DFS
from algo.dijkstra import dijkstra_search, init_map as dijkstra_init_map
# from algo.rl.train import rl
from typing import Optional

from env.environment import Env


def start_search(max_fuel: int,
                 fuel_cost: int,
                 cur_algorithm: AlgoType,
                 forbidden_area: set[tuple[int, int]],
                 carrier_airport_list: list[tuple[int, int]],
                 tanker_list: list[tuple[int, int]],
                 start_pos: tuple[int, int],
                 end_pos: tuple[int, int],
                 map_size: tuple[int, int]) -> [list[tuple[int, int]], Optional[list[int]], Optional[list[list, float]]]:
    path: [list[tuple[int, int]], Optional[list[int]]]
    # reinforcement learning has difficulty in implementation, the code can be check in algo/rl directory
    # if cur_algorithm == AlgoType.RL:
    #     env = Env(max_fuel, fuel_cost, cur_algorithm, forbidden_area, carrier_airport_list, tanker_list, start_pos,
    #               end_pos, map_size)
    #     env.max_fuel = max_fuel
    #     env.fuel_cost = fuel_cost
    #     env.cur_algorithm = cur_algorithm
    #     env.forbidden_area = forbidden_area
    #     env.carrier_airport = carrier_airport_list
    #     env.tanker = tanker_list
    #     env.start_pos = start_pos
    #     env.destination = end_pos
    #     env.map_size = map_size
    #     path = rl(env)
    if cur_algorithm == AlgoType.BFS:
        path = BFS(max_fuel, fuel_cost, forbidden_area, carrier_airport_list, tanker_list, start_pos, end_pos, map_size)
    elif cur_algorithm == AlgoType.ASTAR:
        path = astar(max_fuel, fuel_cost, forbidden_area, carrier_airport_list, tanker_list, start_pos, end_pos, map_size)
    elif cur_algorithm == AlgoType.DIJKSTRA:
        map_grid = dijkstra_init_map(map_size, forbidden_area, carrier_airport_list, tanker_list)
        path = dijkstra_search(map_grid, start_pos, end_pos, fuel_cost, max_fuel)
    elif cur_algorithm == AlgoType.ADVANCED_DIJKSTRA:
        map_grid = advanced_dijkstra_init_map(map_size, forbidden_area, carrier_airport_list, tanker_list)
        path = advanced_dijkstra_search(map_grid, start_pos, end_pos, fuel_cost, max_fuel)
    elif cur_algorithm == AlgoType.DFS:
        try:
            path = DFS(max_fuel, fuel_cost, forbidden_area, carrier_airport_list, tanker_list, start_pos, end_pos, map_size)
        except RecursionError:
            path = [-1]
    elif cur_algorithm == AlgoType.ALL or cur_algorithm == AlgoType.ALL_WITHOUT_DFS:
        start_DIJ = time.time()
        map_grid = dijkstra_init_map(map_size, forbidden_area, carrier_airport_list, tanker_list)
        path_DIJ = dijkstra_search(map_grid, start_pos, end_pos, fuel_cost, max_fuel)
        end_DIJ = time.time()
        start_ASTAR = time.time()
        path_ASTAR = astar(max_fuel, fuel_cost, forbidden_area, carrier_airport_list, tanker_list, start_pos, end_pos, map_size)
        end_ASTAR = time.time()
        start_BFS = time.time()
        path_BFS = BFS(max_fuel, fuel_cost, forbidden_area, carrier_airport_list, tanker_list, start_pos, end_pos, map_size)
        end_BFS = time.time()
        start_DFS = time.time()
        if cur_algorithm == AlgoType.ALL_WITHOUT_DFS:
            return [path_DIJ, end_DIJ - start_DIJ], [path_ASTAR, end_ASTAR - start_ASTAR], [path_BFS, end_BFS - start_BFS], [[-2], 0]
        try:
            path_DFS = DFS(max_fuel, fuel_cost, forbidden_area, carrier_airport_list, tanker_list, start_pos, end_pos, map_size)
        except RecursionError:
            path_DFS = [-1]
        end_DFS = time.time()
        return [path_DIJ, end_DIJ - start_DIJ], [path_ASTAR, end_ASTAR - start_ASTAR], [path_BFS, end_BFS - start_BFS], [path_DFS, end_DFS - start_DFS]
    else:
        path = []
    return path