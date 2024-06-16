import time

from PySide6.QtCore import QThread, Signal

from algo.algo_brain import start_search
from airway_genius_gui.globals import AlgoType


class CalculationThread(QThread):
    finished_signal = Signal(float)
    result_signal = Signal(list)
    error_signal = Signal(str, str)
    all_signal = Signal(int, float, int, float, int, float, int, float)

    def __init__(self,
                 max_fuel: int,
                 fuel_cost: int,
                 cur_algorithm: AlgoType,
                 forbidden_area_coords_list: list[tuple[int, int]],
                 carrier_airport_list: list[tuple[int, int]],
                 tanker_list: list[tuple[int, int]],
                 start_pos: tuple[int, int],
                 end_pos: tuple[int, int],
                 map_size: tuple[int, int],
                 bounding_box_offset: tuple[int, int]):
        super().__init__()
        self.max_fuel = max_fuel
        self.fuel_cost = fuel_cost
        self.cur_algorithm = cur_algorithm
        self.forbidden_area_coords_list = forbidden_area_coords_list
        self.carrier_airport_list = carrier_airport_list
        self.tanker_list = tanker_list
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.map_size = map_size
        self.bounding_box_offset = bounding_box_offset

    def run(self):
        # apply bounding box offset to all coordinates in the input data
        self.forbidden_area_coords_list = [(pos[0] - self.bounding_box_offset[0], pos[1] - self.bounding_box_offset[1])
                                           for pos in self.forbidden_area_coords_list]
        self.carrier_airport_list = [(pos[0] - self.bounding_box_offset[0], pos[1] - self.bounding_box_offset[1]) for
                                     pos in self.carrier_airport_list]
        self.tanker_list = [(pos[0] - self.bounding_box_offset[0], pos[1] - self.bounding_box_offset[1]) for pos in
                            self.tanker_list]
        self.start_pos = (
        self.start_pos[0] - self.bounding_box_offset[0], self.start_pos[1] - self.bounding_box_offset[1])
        self.end_pos = (self.end_pos[0] - self.bounding_box_offset[0], self.end_pos[1] - self.bounding_box_offset[1])
        start_time = time.time()

        forbidden_area_set = set(self.forbidden_area_coords_list)
        # call algorithm in backend
        if self.cur_algorithm != AlgoType.ALL and self.cur_algorithm != AlgoType.ALL_WITHOUT_DFS:
            path = start_search(self.max_fuel,
                                self.fuel_cost,
                                self.cur_algorithm,
                                forbidden_area_set,
                                self.carrier_airport_list,
                                self.tanker_list,
                                self.start_pos,
                                self.end_pos,
                                self.map_size)
            end_time = time.time()
            if path == [-1]:
                self.error_signal.emit("Recursion Error", "DFS algorithm has reached maximum recursion depth")
                self.finished_signal.emit(end_time - start_time)
                return
            elif path is None:
                path = []
            print(path)
            # apply bounding box offset to all coordinates in the path
            path = [(pos[0] + self.bounding_box_offset[0], pos[1] + self.bounding_box_offset[1]) for pos in path]
            self.finished_signal.emit(end_time - start_time)
            self.result_signal.emit(path)
        else:
            dij, astar, bfs, dfs = start_search(self.max_fuel,
                                                self.fuel_cost,
                                                self.cur_algorithm,
                                                forbidden_area_set,
                                                self.carrier_airport_list,
                                                self.tanker_list,
                                                self.start_pos,
                                                self.end_pos,
                                                self.map_size)
            end_time = time.time()
            self.finished_signal.emit(end_time - start_time)
            dij_path = [(pos[0] + self.bounding_box_offset[0], pos[1] + self.bounding_box_offset[1]) for pos in dij[0]]
            astar_path = [(pos[0] + self.bounding_box_offset[0], pos[1] + self.bounding_box_offset[1]) for pos in astar[0]]
            bfs_path = [(pos[0] + self.bounding_box_offset[0], pos[1] + self.bounding_box_offset[1]) for pos in bfs[0]]
            lengths = [len(dij_path), len(astar_path), len(bfs_path)]
            self.result_signal.emit(dij_path)
            self.result_signal.emit(astar_path)
            self.result_signal.emit(bfs_path)
            dfs_path = dfs[0]
            if dfs_path == [-1]:
                self.error_signal.emit("Recursion Error", "DFS algorithm has reached maximum recursion depth")
                lengths.append(-1)
            elif dfs_path == [-2]:
                lengths.append(-2)
            else:
                dfs_path = [(pos[0] + self.bounding_box_offset[0], pos[1] + self.bounding_box_offset[1]) for pos in dfs_path]
                self.result_signal.emit(dfs_path)
                lengths.append(len(dfs_path))
            self.all_signal.emit(lengths[0], dij[1], lengths[1], astar[1], lengths[2], bfs[1], lengths[3], dfs[1])

