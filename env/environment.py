import math
import random


# Define the Agent class with two subclasses: FighterJet and AdversaryJet
class Agent:
    def __init__(self, position, map_size):
        self.position = position
        self.previous_position = None
        self.action_space = [0, 1, 2, 3]
        self.state_space = [(x, y) for x in range(map_size[0]) for y in range(map_size[1])]
        self.reward = 0

    def fly_up(self):
        self.position = (self.position[0], self.position[1] + 1)

    def fly_down(self):
        self.position = (self.position[0], self.position[1] - 1)

    def fly_left(self):
        self.position = (self.position[0] - 1, self.position[1])

    def fly_right(self):
        self.position = (self.position[0] + 1, self.position[1])

    def get_position(self):
        self.position = (0, 0)

    # Returns the total reward after the loop ends
    def total_reward(self):
        return self.reward

    def perform_action(self, action):
        self.previous_position = self.position
        if action == 0:
            self.fly_up()
        elif action == 1:
            self.fly_down()
        elif action == 2:
            self.fly_left()
        elif action == 3:
            self.fly_right()


class FighterJet(Agent):
    def __init__(self, position, fuel, cost_of_fuel, map_size, start_pos, forbidden, tanker):
        super().__init__(position=position, map_size=map_size)
        # Fuel
        self.fuel = fuel
        self.max_fuel = fuel
        # Fuel consumption per pixel
        self.cost_of_fuel = cost_of_fuel
        self.life = 5
        self.enemy = None  # Instance of the enemy jet
        self.state = [self.position, self.fuel, self.life]
        self.start_pos = start_pos
        self.forbidden = forbidden
        self.tanker = tanker

    # Get the current fuel of the jet
    def get_fuel(self):
        return self.fuel

    # Fuel consumption of the jet
    def consume_fuel(self):
        self.fuel -= self.cost_of_fuel
        if self.fuel <= 0:
            self.life -= 1

    def perform_action(self, action):
        self.previous_position = self.position
        if action == 0:
            self.fly_up()
        elif action == 1:
            self.fly_down()
        elif action == 2:
            self.fly_left()
        elif action == 3:
            self.fly_right()
        self.consume_fuel()

    # Set the enemy jet
    def set_enemy(self, adversary_jet):
        self.enemy = adversary_jet

    # Get the position of the enemy jet
    def get_enemy_position(self):
        if self.enemy:
            return self.enemy.position
        else:
            return None

    # Reward function for the jet, reaching the destination rewards 100, contact with enemy deducts 10 and reduces life by 1, game ends if life is 0, entering forbidden area ends the game and resets reward
    # This method is called after each action
    def reward_func(self, destination, enemy_position):
        if self.position == destination:
            self.reward += 100
        if self.position == enemy_position:
            self.life -= 1
            self.reward -= 10
        # Euclidean distance
        current_distance = math.sqrt(
            (self.position[0] - destination[0]) ** 2 + (self.position[1] - destination[1]) ** 2)
        if self.previous_position is not None and current_distance != 0:
            # Adding absolute value to prevent negative numbers
            previous_distance = math.sqrt(
                (self.previous_position[0] - destination[0]) ** 2 + (self.previous_position[1] - destination[1]) ** 2)
            if current_distance < previous_distance:
                self.reward += 0.01 / current_distance
            else:
                self.reward -= 0.1 / current_distance
        if self.reward < 0:
            self.life -= 1
            self.reward = 0
            self.position = self.start_pos
        if self.position in self.forbidden:
            self.life = 0
            self.reward = 0
        if self.position in self.tanker:
            self.fuel = self.max_fuel


# Enemy jet, searches for the presence of our jet and tracks it
class AdversaryJet(Agent):
    def __init__(self, position=(0, 0), map_size=(10, 10)):
        super().__init__(position, map_size)
        self.position = (0, 0)
        self.target = None  # Instance of our jet

    def set_target(self, fighter_jet):
        self.target = fighter_jet

    # Get the position of our jet
    def track_target(self):
        if self.target:
            return self.target.get_position()
        else:
            return None

    # When the position matches our jet's position, reward is 100, otherwise 0 (forbidden areas do not affect the enemy jet)
    def reward_func(self, target_position):
        if self.position == target_position:
            self.reward += 100

    # Initial position of the enemy jet is random
    def random_position(self, max_width=10, max_height=10):
        self.position = (random.randint(0, max_width), random.randint(0, max_height))


# Use a graph data structure to represent the map, each pixel is a node, carrier represents aircraft carrier with 1, tanker with 2, airport with 3
class Node:
    def __init__(self, type=0):
        self.type = type
        self.visited = 0

    def __str__(self):
        return f"({self.type}, {self.visited})"

    __repr__ = __str__


# Initialize the map, receiving four parameter lists representing forbidden areas, carrier positions, tanker positions, and airport positions
def init_map(forbidden, carrier_airport, tanker):
    map = []
    for i in range(8):
        row = []
        for j in range(8):
            node = Node(type=0)
            # Forbidden area
            if (i, j) in forbidden:
                node.visited = 1
            # Carrier/Airport
            if (i, j) in carrier_airport:
                node.type = 1
            # Tanker
            if (i, j) in tanker:
                node.type = 2
            row.append(node)
        map.append(row)
    return map


# Initialize the fighter jet
def init_fighter_jet(position, fuel, cost_of_fuel, map_size, start_pos, forbidden, tanker):
    return FighterJet(position, fuel, cost_of_fuel, map_size, start_pos, forbidden, tanker)


# Initialize the enemy jet
def init_adversary_jet():
    return AdversaryJet()


# Initialize the environment
class Env:
    def __init__(self, max_fuel,
                 fuel_cost,
                 cur_algorithm,
                 forbidden_area,
                 carrier_airport_list,
                 tanker_list,
                 start_pos,
                 end_pos,
                 map_size):
        self.map_size = map_size
        self.max_fuel = max_fuel
        self.fuel_cost = fuel_cost
        self.cur_algorithm = cur_algorithm
        self.forbidden_area = forbidden_area
        self.carrier_airport = carrier_airport_list
        self.tanker = tanker_list
        self.start_pos = start_pos
        self.destination = end_pos
        self.fighter_jet = init_fighter_jet(self.start_pos, self.max_fuel, self.fuel_cost, self.map_size, self.start_pos, self.forbidden_area, self.tanker)
        self.adversary_jet = init_adversary_jet()
        self.map = init_map(self.forbidden_area, self.carrier_airport, self.tanker)
        self.fighter_jet.position = self.start_pos

    # Reset the environment, reset the position and score of the jet
    def reset(self):
        self.fighter_jet.position = self.start_pos
        self.fighter_jet.reward = 0
        self.fighter_jet.life = 5
        self.fighter_jet.fuel = self.max_fuel
        self.fighter_jet.state = [self.fighter_jet.position, self.fighter_jet.fuel, self.fighter_jet.life]
        self.adversary_jet.position = (0, 0)
        self.adversary_jet.reward = 0
        self.adversary_jet.target = self.fighter_jet
        return self.fighter_jet.state

    def step(self, action):
        self.fighter_jet.perform_action(action)
        self.fighter_jet.consume_fuel()

        # Update state
        self.fighter_jet.state = [self.fighter_jet.position, self.fighter_jet.fuel, self.fighter_jet.life]

        # Update rewards
        self.fighter_jet.reward_func(self.destination, self.adversary_jet.position)

        done = self.fighter_jet.position == self.destination

        truncated = self.fighter_jet.life <= 0 or self.fighter_jet.position in self.forbidden_area or self.fighter_jet.fuel <= 0
        return self.fighter_jet.state, self.fighter_jet.reward, truncated, done, None


def read_data():
    with open("data.txt", "r") as f:
        data = f.readlines()
    return [x.split(":")[1].strip() for x in data]

