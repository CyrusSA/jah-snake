import networkx as nx
from collections import OrderedDict
import random

'''To-do
- Account for growth after eating - DONE ish
- debug
- Dont go for food unless path to tail - DONE
- Dont go for food if enemy can get there first unless low health or longer than enemy by a margin
- Chase enemy tail sometime
- Be aggressive with food early on?
'''

class Game:
    def __init__(self, game_data):
        self.board_height = game_data['board']['height']
        self.board_width = game_data['board']['width']
        self.health = 100
        self.head = ("", "")
        self.tail = ("", "")
        self.board = nx.Graph()
        self.foods = []
        self.snakes = []
        self.my_length = 0
        self.health_threshold = 80

    # Updates game state with data from /move request.
    def update_game(self, game_data):
        self.head = (game_data["you"]["body"][0]["x"], game_data["you"]["body"][0]["y"])
        self.tail = (game_data["you"]["body"][-1]["x"], game_data["you"]["body"][-1]["y"])
        self.my_length =  len(list(OrderedDict.fromkeys([str(point["x"]) + str(point["y"]) for point in game_data['you']['body']])))
        self.health = game_data["you"]["health"]
        self.just_ate = (self.health == 100 and game_data["turn"] > 0)
        self.foods = [(food["x"], food["y"]) for food in game_data["board"]["food"]]
        self.update_snakes(game_data)
        self.update_board()

    # Populate self.snakes with snake data.
    # If turn 0, don't add any of me
    # If just ate, don't add tail
    # Else don't add my head and tail
    def update_snakes(self, game_data):
        self.snakes = []
        for snake in game_data["board"]["snakes"]:
            # Add all snakes except me to self.snakes
            if snake["id"] != game_data["you"]["id"]:
                self.snakes.extend([(point["x"], point["y"]) for point in snake["body"]])
                x = snake["body"][0]["x"]
                y = snake["body"][0]["y"]
                for node in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
                    if node not in self.snakes:
                        self.snakes.append(node)
        if game_data["turn"] == 0 or game_data["turn"] == 1:
            return
        self.snakes.extend([(point["x"], point["y"]) for point in game_data["you"]["body"][1:(-2 if self.just_ate else -1)]])

    # Creates and populates graph of board points. Does not add a point if it houses a snake.
    def update_board(self):
        self.board = nx.Graph()
        for y in range(self.board_height):
            for x in range(self.board_width):
                current_node = (x, y)
                if current_node in self.snakes:
                    continue
                self.board.add_node(current_node)
                self.add_edges(current_node)

    # Connects nodes if the potential node is already in the graph.
    # If my length is 2, do not connect head and tail.
    # Else connect
    def add_edges(self, current_node):
        x = current_node[0]
        y = current_node[1]
        for node in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
            if self.board.has_node(node):
                if self.my_length == 2 :
                    if (current_node not in [self.head, self.tail]) or (node not in [self.head, self.tail]):
                        self.board.add_edge(node, current_node)
                else:
                    self.board.add_edge(node, current_node)

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

            shortest_path = nx.shortest_path(self.board, self.head, self.tail)
            destination = shortest_path[1]

            # Two body points stacked at tail, don't follow closely
            if self.just_ate and destination == self.tail:
                for path in nx.all_simple_paths(self.board, self.head, self.tail, 4):
                    if len(path) > 3:
                        destination = path[1]
                        break
                if destination == self.tail:
                    print("No alternate paths")

            return self.get_direction(destination)
        except nx.NodeNotFound:
            print("NO OPTIONS RANDOM DIRECTION")
            return self.get_direction(random.choice(list(self.board)))

    # Gets destination of closest food item
    def get_food_destination(self):
        shortest_food_path = []
        for food_path in [nx.shortest_path(self.board, self.head, food) for food in self.foods if self.board.has_node(food)]:
            if len(food_path) < len(shortest_food_path) or len(shortest_food_path) == 0:
                try:
                    nx.shortest_path(self.board, food_path[-1], self.tail)
                except nx.NetworkXNoPath:
                    continue
                shortest_food_path = food_path
        return shortest_food_path

    # Returns direction to turn in order to reach destination
    def get_direction(self, destination):
        if self.head[0] == destination[0]:
            if self.head[1] > destination[1]:
                return 'up'
            return 'down'
        if self.head[0] > destination[0]:
            return 'left'
        return 'right'

    # get path to closest enemy tail
    def get_enemy_tail_destination(self, game_data):
        enemy_tails = []
        # add the last body point of every snake except me to enemy_tails
        for snake in game_data["board"]["snakes"]:
            if snake["id"] != game_data["you"]["id"]:
                enemy_tails.append((snake["body"][-1]["x"], snake["body"][-1]["y"]))
        # remove tails with no path
        for tail in enemy_tails:
            try:
                last_path = nx.shortest_path(self.board, self.head, tail)
            except nx.NetworkXNoPath:
                enemy_tails.remove(tail)
        # find and return shortest path
        shortest_path = last_path
        for tail in enemy_tails:
            path = nx.shortest_path(self.board, self.head, tail)
            if len(path) < len(shortest_path):
                shortest_path = path
        return shortest_path
