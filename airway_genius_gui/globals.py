import os
from enum import Enum

from PySide6.QtGui import QColor

GUI_DIR = os.path.dirname(__file__)


class MarkerType(Enum):
    """
    Enum class for marker types and colors.
    """
    NONE_TYPE = 0
    CARRIER = QColor(63, 203, 117, 255)
    TANKER = QColor(30, 155, 228, 255)
    AIRPORT = QColor(232, 94, 110, 255)


class MapType(Enum):
    """
    Enum class for map
    """
    CHINA = 'China'
    EURASIA = 'Eurasia'
    AFRICA = 'Africa'
    AUSTRALIA = 'Australia'
    NORTH_AMERICA = 'NorthAmerica'


class OtherColor(Enum):
    PATH_COLOR = QColor(98, 88, 224, 255)
    FORBIDDEN_AREA_COLOR = QColor(255, 131, 28, 255)


class AlgoType(Enum):
    """
    Enum class for algorithm
    """
    BFS = 'BFS'
    DFS = 'DFS(may be slow)'
    ASTAR = 'A*'
    DIJKSTRA = 'Dijkstra'
    ADVANCED_DIJKSTRA = 'Dijkstra(Visually-Optimized)'
    ALL_WITHOUT_DFS = 'All(without DFS)'
    ALL = 'All(may be slow)'
    # reinforcement learning has difficulty in implementation, the code can be check in algo/rl directory
    # RL = 'Reinforcement Learning'


cur_marker_type = MarkerType.NONE_TYPE


def set_cur_marker_type(marker_type):
    """
    Set the current marker type
    """
    global cur_marker_type
    cur_marker_type = marker_type


def get_cur_marker_type():
    """
    Get the current marker type
    """
    return cur_marker_type


def get_bounding_box(data: list[8]):
    """
    Get the bounding box of the map
    """
    forbidden_area, carrier_airport_list, tanker_list, map_size = data[3], data[4], data[5], data[8]
    x_coords = [pos[0] for pos in forbidden_area + carrier_airport_list + tanker_list]
    y_coords = [pos[1] for pos in forbidden_area + carrier_airport_list + tanker_list]
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    map_width, map_height = max_x - min_x + 3, max_y - min_y + 3
    offset_x, offset_y = min_x - 1, min_y - 1
    if max_x >= map_size[0] - 1:
        map_width -= 1
    if max_y >= map_size[1] - 1:
        map_height -= 1
    if min_x == 0:
        map_width -= 1
        offset_x = 0
    if min_y == 0:
        map_height -= 1
        offset_y = 0
    data[8] = (map_width, map_height)
    data.append((offset_x, offset_y))
