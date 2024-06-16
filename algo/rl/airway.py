from contextlib import closing
from io import StringIO
from os import path
from typing import List, Optional

import numpy as np

import gymnasium as gym
from gymnasium import Env, spaces, utils
from gymnasium.envs.toy_text.utils import categorical_sample
from gymnasium.error import DependencyNotInstalled
from gymnasium.utils import seeding
from gymnasium.envs.registration import register
import sys

LEFT = 0
DOWN = 1
RIGHT = 2
UP = 3

MAPS = {
    "4x4": ["SCCC", "CTCF", "CCCF", "FCCD"],
    "8x8": [
        "SCCCCCCC",
        "CCCCCCCC",
        "CCCTCCCC",
        "CCCCCTCC",
        "CCCTCCCC",
        "CFFCTCFC",
        "CFCCFCFC",
        "CCCFCCCD",
    ],
}


def is_valid(board: List[List[str]], max_length: int, max_width: int) -> bool:
    frontier, discovered = [], set()
    frontier.append((0, 0))
    while frontier:
        r, c = frontier.pop()
        if not (r, c) in discovered:
            discovered.add((r, c))
            directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
            for x, y in directions:
                r_new = r + x
                c_new = c + y
                if r_new < 0 or r_new >= max_length or c_new < 0 or c_new >= max_width:
                    continue
                if board[r_new][c_new] == "D":
                    return True
                if board[r_new][c_new] != "F":
                    frontier.append((r_new, c_new))
    return False


def read_data():
    with open("data.TXT", "r") as f:
        data = f.readlines()
    return [x.split(" = ")[1].strip() for x in data]


def generate_random_map(width: int = 240, length: int = 108, p: float = 0.8, seed: Optional[int] = None) -> List[str]:
    """Generates a random valid map (one that has a path from start to goal)

    Args:
        size: size of each side of the grid (240*108)
        p: probability that a tile is safe
        seed: optional seed to ensure the generation of reproducible maps

    Returns:
        A random valid map
    """
    # valid = False
    # board = []
    board = [["C" for _ in range(width)] for _ in range(length)]

    np_random, _ = seeding.np_random(seed)

    data = read_data()

    no_fly_zone = eval(data[2])
    refuel_stations = eval(data[4])

    # Set start and destination
    start = (36, 1)
    destination = (33, 238)
    board[start[0]][start[1]] = "S"
    board[destination[0]][destination[1]] = "D"

    # Set no-fly zones
    for (r, c) in no_fly_zone:
        board[c][r] = "F"

    # Set refuel stations
    tanker = []
    for (r, c) in refuel_stations:
        board[c][r] = "T"
        tanker.append((r, c))

    # Ensure the map is valid
    assert is_valid(board, length, width), "Generated map is not valid."

    return ["".join(x) for x in board], start, destination, tanker

    # while not valid:
    #     p = min(1, p)
    #     board = np_random.choice(["C", "F", "T"], (length, width), p=[p, 0.9 - p, 0.1]).tolist()
    #     board[1][36] = "S"
    #     board[238][33] = "D"
    #     valid = is_valid(board, length, width)
    # return ["".join(x) for x in board]


class AirwayEnv(Env):
    """
    Planes fly from start to finish, with no-fly zones and gas stations on the way.
    S: Starting point
    C: Secure area
    F: No fly zone
    T: Gas station
    D: End point
    Each time the moving oil amount is reduced by 1, the oil amount is filled to 270 at the gas station,
    the oil amount fails to run out, and the failure to enter the no-fly zone.
    ## Action Space
    The action shape is `(1,)` in the range `{0, 3}` indicating
    which direction to move the player.

    - 0: Move left
    - 1: Move down
    - 2: Move right
    - 3: Move up

    ## Observation Space
    The observation is a value representing the player's current position as
    current_row * nrows + current_col (where both the row and col start at 0).

    For example, the goal position in the 4x4 map can be calculated as follows: 3 * 4 + 3 = 15.
    The number of possible observations is dependent on the size of the map.

    The observation is returned as an `int()`.

    ## Starting State
    The episode starts with the player in state `[0]` (location [0, 0]).

    ## Rewards

    Reward schedule:
    - Reach destination(D): +1
    - Reach forbidden(F): 0
    - Reach tanker(T): +0.5

     ## Episode End
    The episode ends if the following happens:

    - Termination:
        1. The plane moves into a forbidden.
        2. The plane reaches the destination at `max(nrow) * max(ncol) - 1` (location `[max(nrow)-1, max(ncol)-1]`).

    - Truncation (when using the time_limit wrapper):
        1. The length of the episode is 100 for 4x4 environment, 200 for FrozenLake8x8-v1 environment.

    ## Information

    `step()` and `reset()` return a dict with the following keys:
    - p - transition probability for the state.

    ## Arguments

    ```python
    import gymnasium as gym
    gym.make('Airway-v1', desc=None, map_name="4x4")
    ```

    `desc=None`: Used to specify maps non-preloaded maps.

    Specify a custom map.
    ```
        desc=["SFFF", "FHFH", "FFFH", "HFFG"].
    ```

    A random generated map can be specified by calling the function `generate_random_map`.
    ```
    from gymnasium.envs.user.airway import generate_random_map

    gym.make('Airway-v1', desc=generate_random_map(lenth=240, width=108))
    ```

    `map_name="4x4"`: ID to use any of the preloaded maps.
    ```
        "4x4":[
            "SCCC",
            "CFCF",
            "CCCF",
            "FCCD"
            ]

        "8x8": [
            "SCCCCCCC",
            "CCCCCCCC",
            "CCCFCCCC",
            "CCCCCFCC",
            "CCCFCCCC",
            "CFFCCCFC",
            "CFCCFCFC",
            "CCCFCCCD",
        ]
    ```
    """
    metadata = {"render_modes": ["human", "ansi", "rgb_array"],
                "render_fps": 4, }

    def __init__(
            self,
            render_mode: Optional[str] = None,
            desc=None,
            map_name="4x4",
            fuel_capacity=270
    ):
        if desc is None and map_name is None:
            desc, self.start, self.goal, self.tanker = generate_random_map()
        elif desc is None:
            desc = MAPS[map_name]
        self.desc = desc = np.asarray(desc, dtype="c")
        self.nrow, self.ncol = nrow, ncol = desc.shape
        self.reward_range = (0, 1)

        self.prev_s = None
        self.path = []

        nA = 4
        nS = nrow * ncol

        self.initial_state_distrib = np.array(desc == b"S").astype("float64").ravel()
        self.initial_state_distrib /= self.initial_state_distrib.sum()

        self.P = {s: {a: [] for a in range(nA)} for s in range(nS)}

        self.fuel_capacity = fuel_capacity
        self.fuel = fuel_capacity

        # self.P = {s: {a: [] for a in range(4)} for s in range(nrow * ncol)}
        # self._init_probability_matrix(desc, nrow, ncol)
        #
        # self.s = categorical_sample([1.0] * (nrow * ncol), self.np_random)
        # self.lastaction = None

        def to_s(row, col):
            return row * ncol + col

        def inc(row, col, a):
            if a == LEFT:
                col = max(col - 1, 0)
            elif a == DOWN:
                row = min(row + 1, nrow - 1)
            elif a == RIGHT:
                col = min(col + 1, ncol - 1)
            elif a == UP:
                row = max(row - 1, 0)
            return (row, col)

        def update_probability_matrix(row, col, action):
            newrow, newcol = inc(row, col, action)
            newstate = to_s(newrow, newcol)
            newletter = desc[newrow, newcol]
            terminated = bytes(newletter) in b"DF"
            reward = bytes(newletter) in b"DT"
            if newletter == b"D":
                reward = 100
            elif newletter == b"T":
                reward = 5
            else:
                reward = 0.0

            goal_row, goal_col = self.goal  # Assuming 'goal' is a tuple (row, col)
            distance_to_goal = ((newrow - goal_row) ** 2 + (newcol - goal_col) ** 2) ** 0.5
            reward += 1 / (distance_to_goal + 1)  # The '+1' in the denominator is to prevent division by zero

            # If fuel is less than a threshold, add a small reward for getting closer to the tanker
            if self.fuel < 50:  # Assuming the threshold is 50
                tanker_row, tanker_col = self.tanker[0]  # Assuming 'tanker' is a tuple (row, col)
                distance_to_tanker = ((newrow - tanker_row) ** 2 + (newcol - tanker_col) ** 2) ** 0.5
                reward += 2 / (distance_to_tanker + 1)  # The '+1' in the denominator is to prevent division by zero
            return newstate, reward, terminated

        for row in range(nrow):
            for col in range(ncol):
                s = to_s(row, col)
                for a in range(4):
                    li = self.P[s][a]
                    letter = desc[row][col]
                    if letter in b"DFT":
                        li.append((1.0, s, 0, True))
                    else:
                        li.append((1.0, *update_probability_matrix(row, col, a)))

        self.observation_space = spaces.Discrete(nS)
        self.action_space = spaces.Discrete(nA)

        self.render_mode = render_mode

        # pygame utils
        self.window_size = (min(8 * ncol, 1920), min(8 * nrow, 864))
        self.cell_size = (
            self.window_size[0] // self.ncol,
            self.window_size[1] // self.nrow,
        )
        self.window_surface = None
        self.clock = None
        self.hole_img = None  # no-fly zone
        self.cracked_hole_img = None
        self.ice_img = None
        self.elf_images = None
        self.goal_img = None
        self.start_img = None
        self.tanker_img = None
        self.background = None

    def reset(
            self,
            *,
            seed: Optional[int] = None,
            options: Optional[dict] = None,
    ):
        super().reset(seed=seed)
        self.s = categorical_sample(self.initial_state_distrib, self.np_random)
        self.lastaction = None
        self.fuel = self.fuel_capacity

        if self.render_mode == "human":
            self.render()
        return int(self.s), {"prob": 1}

    def _start_state(self):
        return 0

    def step(self, a):
        transitions = self.P[self.s][a]
        i = categorical_sample([t[0] for t in transitions], self.np_random)
        p, s, r, t = transitions[i]
        self.prev_s = self.s
        self.s = s
        self.lastaction = a
        self.path.append(self.s)

        if self.desc[s // self.ncol][s % self.ncol] == b"T":
            self.fuel = self.fuel_capacity
        else:
            self.fuel -= 1

        if self.fuel <= 0:
            t = True
            r = 0

        if self.render_mode == "human":
            self.render()
        return (int(s), r, t, False, {"prob": p})

    def render(self):
        if self.render_mode is None:
            assert self.spec is not None
            gym.logger.warn(
                "You are calling render method without specifying any render mode. "
                "You can specify the render_mode at initialization, "
                f'e.g. gym.make("{self.spec.id}", render_mode="rgb_array")'
            )
            return

        if self.render_mode == "ansi":
            return self._render_text()
        else:  # self.render_mode in {"human", "rgb_array"}:
            return self._render_gui(self.render_mode)

    def _render_gui(self, mode):
        try:
            import pygame
        except ImportError as e:
            raise DependencyNotInstalled(
                "pygame is not installed, run `pip install gymnasium[toy-text]`"
            ) from e

        if self.window_surface is None:
            pygame.init()

            if mode == "human":
                pygame.display.init()
                pygame.display.set_caption("Airway Genius")
                self.window_surface = pygame.display.set_mode(self.window_size)
            elif mode == "rgb_array":
                self.window_surface = pygame.Surface(self.window_size)

        assert (
                self.window_surface is not None
        ), "Something went wrong with pygame. This should never happen."

        if self.clock is None:
            self.clock = pygame.time.Clock()
        if self.hole_img is None:
            file_name = path.join(path.dirname(__file__), "img/hole.png")
            self.hole_img = pygame.transform.scale(
                pygame.image.load(file_name), self.cell_size
            )
        if self.cracked_hole_img is None:
            file_name = path.join(path.dirname(__file__), "img/cracked_hole.png")
            self.cracked_hole_img = pygame.transform.scale(
                pygame.image.load(file_name), self.cell_size
            )
        if self.ice_img is None:
            file_name = path.join(path.dirname(__file__), "img/ice.png")
            self.ice_img = pygame.transform.scale(
                pygame.image.load(file_name), self.cell_size
            )
        if self.goal_img is None:
            file_name = path.join(path.dirname(__file__), "img/goal.png")
            self.goal_img = pygame.transform.scale(
                pygame.image.load(file_name), self.cell_size
            )
        if self.tanker_img is None:
            file_name = path.join(path.dirname(__file__), "img/cab_rear.png")
            self.tanker_img = pygame.transform.scale(
                pygame.image.load(file_name), self.cell_size
            )
        if self.start_img is None:
            file_name = path.join(path.dirname(__file__), "img/stool.png")
            self.start_img = pygame.transform.scale(
                pygame.image.load(file_name), self.cell_size
            )
        if self.background is None:
            file_name = path.join(path.dirname(__file__), "img/china.png")
            self.background = pygame.transform.scale(
                pygame.image.load(file_name), self.window_size
            )
        if self.elf_images is None:
            elfs = [
                path.join(path.dirname(__file__), "img/elf_left.png"),
                path.join(path.dirname(__file__), "img/elf_down.png"),
                path.join(path.dirname(__file__), "img/elf_right.png"),
                path.join(path.dirname(__file__), "img/elf_up.png"),
            ]
            self.elf_images = [
                pygame.transform.scale(pygame.image.load(f_name), self.cell_size)
                for f_name in elfs
            ]

        desc = self.desc.tolist()
        assert isinstance(desc, list), f"desc should be a list or an array, got {desc}"
        self.window_surface.blit(self.background, (0, 0))
        for y in range(self.nrow):
            for x in range(self.ncol):
                pos = (x * self.cell_size[0], y * self.cell_size[1])
                rect = (*pos, *self.cell_size)

                # self.window_surface.blit(self.ice_img, pos)
                if desc[y][x] == b"F":
                    self.window_surface.blit(self.hole_img, pos)
                elif desc[y][x] == b"D":
                    self.window_surface.blit(self.goal_img, pos)
                elif desc[y][x] == b"S":
                    self.window_surface.blit(self.start_img, pos)
                elif desc[y][x] == b"T":
                    self.window_surface.blit(self.tanker_img, pos)

                # pygame.draw.rect(self.window_surface, (180, 200, 230), rect, 1)

        # paint the elf
        bot_row, bot_col = self.s // self.ncol, self.s % self.ncol
        cell_rect = (bot_col * self.cell_size[0], bot_row * self.cell_size[1])
        last_action = self.lastaction if self.lastaction is not None else 1
        elf_img = self.elf_images[last_action]

        if desc[bot_row][bot_col] == b"F":
            self.window_surface.blit(self.cracked_hole_img, cell_rect)
        else:
            self.window_surface.blit(elf_img, cell_rect)

        # for s in self.path:
        #     row, col = s // self.ncol, s % self.ncol
        #     pos = (col * self.cell_size[0], row * self.cell_size[1])
        #     pygame.draw.circle(self.window_surface, (255, 0, 0), pos, 5)

        for idx in range(1, len(self.path)):
            start_state = self.path[idx - 1]
            end_state = self.path[idx]
            start_pos = (
                (start_state % self.ncol) * self.cell_size[0] + self.cell_size[0] // 2,
                (start_state // self.ncol) * self.cell_size[1] + self.cell_size[1] // 2,
            )
            end_pos = (
                (end_state % self.ncol) * self.cell_size[0] + self.cell_size[0] // 2,
                (end_state // self.ncol) * self.cell_size[1] + self.cell_size[1] // 2,
            )
            pygame.draw.line(self.window_surface, (255, 0, 0), start_pos, end_pos, 3)

        if mode == "human":
            pygame.event.pump()
            pygame.display.update()
            self.clock.tick(self.metadata["render_fps"])
        elif mode == "rgb_array":
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(self.window_surface)), axes=(1, 0, 2)
            )

    @staticmethod
    def _center_small_rect(big_rect, small_dims):
        offset_w = (big_rect[2] - small_dims[0]) / 2
        offset_h = (big_rect[3] - small_dims[1]) / 2
        return (
            big_rect[0] + offset_w,
            big_rect[1] + offset_h,
        )

    def _render_text(self):
        desc = self.desc.tolist()
        outfile = StringIO()

        row, col = self.s // self.ncol, self.s % self.ncol
        desc = [[c.decode("utf-8") for c in line] for line in desc]
        desc[row][col] = utils.colorize(desc[row][col], "red", highlight=True)
        if self.lastaction is not None:
            outfile.write(f"  ({['Left', 'Down', 'Right', 'Up'][self.lastaction]})\n")
        else:
            outfile.write("\n")
        outfile.write("\n".join("".join(line) for line in desc) + "\n")

        with closing(outfile):
            return outfile.getvalue()

    def close(self):
        if self.window_surface is not None:
            import pygame

            pygame.display.quit()
            pygame.quit()


import sys
import os

sys.path.append(os.path.dirname(__file__))

register(
    id="Airway-v",
    entry_point="algo.rl.airway:AirwayEnv",
)

if __name__ == "__main__":
    env = gym.make('Airway-v0', render_mode="human", desc=None, map_name=None)
    env.reset()
    for _ in range(100):
        env.render()
        action = env.action_space.sample()  # take a random action
        env.step(action)
