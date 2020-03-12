import networkx as nx
from collections import OrderedDict
import random

'''To-do
- Dont go for food unless path to tail - check ahead a step
- Dont go for food if enemy can get there first unless low health or longer than enemy by a margin
- go to possible enemy next move only if longer than enemy
- If no paths, add enemy next moves to board
'''

class Game:
    def __init__(self, game_data):
        self.board_height = game_data['board']['height']
        self.board_width = game_data['board']['width']
        self.health = 100
        self.head = ("", "")
        self.tail = ("", "")
        self.no_tails_board = nx.Graph()
        self.my_tail_board = nx.Graph()
        self.enemy_tails_board = nx.Graph()
        self.foods = []
        self.snakes = []
        self.my_length = 0
        self.health_threshold = 99
        self.just_ate = False

    # Updates game state with data from /move request.
    def update_game(self, game_data):
        self.game_data = game_data
        self.head = (self.game_data["you"]["body"][0]["x"], self.game_data["you"]["body"][0]["y"])
        self.tail = (self.game_data["you"]["body"][-1]["x"], self.game_data["you"]["body"][-1]["y"])
        self.my_length =  len(list(OrderedDict.fromkeys([str(point["x"]) + str(point["y"]) for point in self.game_data['you']['body']])))
        self.health = self.game_data["you"]["health"]
        self.just_ate = (self.health == 100 and self.game_data["turn"] > 0)
        self.foods = [(food["x"], food["y"]) for food in self.game_data["board"]["food"]]
        self.update_snakes()
        self.no_tails_board = self.update_board(self.extend_and_return_snakes(self.get_tails()))
        self.my_tail_board = self.update_board(self.extend_and_return_snakes(self.get_tails(True)))
        self.enemy_tails_board = self.update_board(self.extend_and_return_snakes([self.tail]))

    # Populate self.snakes with snake data.
    # If turn 0, don't add any of me
    # If just ate, don't add tail
    # Else don't add my head and tail
    def update_snakes(self):
        self.snakes = []
        for snake in self.game_data["board"]["snakes"]:
            # Add all snakes except me to self.snakes
            if snake["id"] != self.game_data["you"]["id"]:
                self.snakes.extend([(point["x"], point["y"]) for point in snake["body"][:-1]])
                x = snake["body"][0]["x"]
                y = snake["body"][0]["y"]
                for node in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
                    if node not in self.snakes:
                        self.snakes.append(node)
        if self.game_data["turn"] == 0 or self.game_data["turn"] == 1:
            return
        self.snakes.extend([(point["x"], point["y"]) for point in self.game_data["you"]["body"][1:(-2 if self.just_ate else -1)] if point not in self.snakes])

    # Creates and populates graph of board points. Does not add a point if it houses a snake.
    def update_board(self, snakes):
        board = nx.Graph()
        for y in range(self.board_height):
            for x in range(self.board_width):
                current_node = (x, y)
                if current_node in snakes:
                    continue
                board.add_node(current_node)
                self.add_edges(board, current_node)
        return board

    # Connects nodes if the potential node is already in the graph.
    # If my length is 2, do not connect head and tail.
    # Else connect
    def add_edges(self, board, current_node):
        x = current_node[0]
        y = current_node[1]
        for node in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
            if board.has_node(node):
                if self.my_length == 2 :
                    if (current_node not in [self.head, self.tail]) or (node not in [self.head, self.tail]):
                        board.add_edge(node, current_node)
                else:
                    board.add_edge(node, current_node)

    # Returns direction to turn. If health is below threshold, move will be towards closest food item.
    # Else if turn 0, return default move
    # Else move towards tail
    def get_move(self):
        try:
            if self.my_length == 1:
                return 'up'
            if self.health < self.health_threshold:
                try:
                    shortest_food_path = self.get_food_destination()
                    if shortest_food_path:
                        return self.get_direction(shortest_food_path[1])
                except nx.NetworkXNoPath:
                    pass

            try:
                shortest_tail_path = nx.shortest_path(self.my_tail_board, self.head, self.tail)
                if shortest_tail_path:
                    destination = shortest_tail_path[1]
                    return self.get_direction(destination)
            except nx.NetworkXNoPath:
                pass

            # Two body points stacked at tail, don't follow closely
            if self.just_ate and destination == self.tail:
                for path in nx.all_simple_paths(self.my_tail_board, self.head, self.tail, 4):
                    if len(path) > 3:
                        destination = path[1]
                        break
                if destination == self.tail:
                    print("No alternate paths")

            # else chase enemy tail
            shortest_enemy_tail_path = self.get_enemy_tail_destination()
            if shortest_enemy_tail_path:
                return self.get_direction(shortest_enemy_tail_path[1])

            # return direction
            return self.get_direction(destination)
        except nx.NodeNotFound:
            print("NO OPTIONS RANDOM DIRECTION")
            return self.get_direction(random.choice(list(self.no_tails_board)))

    # Gets destination of closest food item
    def get_food_destination(self):
        shortest_food_path = []
        for food_path in [nx.shortest_path(self.no_tails_board, self.head, food) for food in self.foods if self.no_tails_board.has_node(food)]:
            if len(food_path) < len(shortest_food_path) or len(shortest_food_path) == 0:
                try:
                    nx.shortest_path(self.my_tail_board, food_path[-1], self.tail)
                except nx.NetworkXNoPath:
                    continue
                shortest_food_path = food_path
        return shortest_food_path

    # get path to closest enemy tail
    def get_enemy_tail_destination(self):
        # remove tail with no path
        enemy_tail_paths = []
        for tail in self.get_tails(True):
            try:
                enemy_tail_paths.append(nx.shortest_path(self.enemy_tails_board, self.head, tail))
            except nx.NetworkXNoPath:
                pass
        # find and return shortest path
        shortest_path = []
        if enemy_tail_paths:
            shortest_path = enemy_tail_paths[0]
            for path in enemy_tail_paths:
                if len(path) < len(shortest_path):
                    shortest_path = path
        return shortest_path

    def get_tails(self, enemy_only=False):
        tails = []
        # add the last body point of every snake except me to tails
        for snake in self.game_data["board"]["snakes"]:
            if snake["id"] == self.game_data["you"]["id"] and enemy_only:
                continue
            tails.append((snake["body"][-1]["x"], snake["body"][-1]["y"]))
        return tails

    # Returns direction to turn in order to reach destination
    def get_direction(self, destination):
        if self.head[0] == destination[0]:
            if self.head[1] > destination[1]:
                return 'up'
            return 'down'
        if self.head[0] > destination[0]:
            return 'left'
        return 'right'

    def extend_and_return_snakes(self, extension):
        new_list = self.snakes[:]
        new_list.extend(extension)
        return new_list
