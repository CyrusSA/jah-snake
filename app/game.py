import networkx as nx
from collections import OrderedDict
import random


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
        self.health_threshold = 75

    # Updates game state with data from /move request.
    def update_game(self, game_data):
        self.head = (game_data["you"]["body"][0]["x"], game_data["you"]["body"][0]["y"])
        self.tail = (game_data["you"]["body"][-1]["x"], game_data["you"]["body"][-1]["y"])
        self.my_length = self.get_my_length(game_data["you"]["body"])
        self.foods = [(food["x"], food["y"]) for food in game_data["board"]["food"]]
        self.update_snakes(game_data)
        self.update_board()
        self.health = game_data["you"]["health"]

    # Populate self.snakes with snake data.
    # If turn 0, don't add any of me
    # Else don't add my head and tail
    def update_snakes(self, game_data):
        for snake in game_data["board"]["snakes"]:
            # Add all snakes except me to self.snakes
            self.snakes = [(point["x"], point["y"]) for point in snake["body"] if snake["id"] != game_data["you"]["id"]]
            if snake["id"] != game_data["you"]["id"]:
                x = snake["body"][0]["x"]
                y = snake["body"][0]["y"]
                for node in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
                    if node not in self.snakes:
                        self.snakes.append(node)
        if game_data["turn"] == 0 or game_data["turn"] == 1:
            return
        else:
            self.snakes.extend([(point["x"], point["y"]) for point in game_data["you"]["body"][1:-1]])

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
                    destination = self.get_food_destination()
                except nx.NetworkXNoPath:
                    if not self.board.has_node(self.tail):
                        self.board.add_node(self.tail)
                        self.add_edges(self.tail)
                    destination = nx.shortest_path(self.board, self.head, self.tail)[1]
            else:
                if not self.board.has_node(self.tail):
                    self.board.add_node(self.tail)
                    self.add_edges(self.tail)
                shortest_path = nx.shortest_path(self.board, self.head, self.tail)
                destination = shortest_path[1]
                # if self.health == 100 and len(shortest_path) == 2:
                #     x = self.head[0]
                #     y = self.tail[1]
            return self.get_direction(destination)
        except nx.NodeNotFound:
            return self.get_direction(random.choice(self.board.nodes()))

    # Gets destination of closest food item
    def get_food_destination(self):
        shortest_food_path = [i for i in range(1000)]
        for food_path in [nx.shortest_path(self.board, self.head, food) for food in self.foods]:
            if len(food_path) < len(shortest_food_path):
                shortest_food_path = food_path
        return shortest_food_path[1]

    # Returns direction to turn in order to reach destination
    def get_direction(self, destination):
        if self.head[0] == destination[0]:
            if self.head[1] > destination[1]:
                return 'up'
            return 'down'
        if self.head[0] > destination[0]:
            return 'left'
        return 'right'

    # Pretty fucking obvious innit
    def get_my_length(self, my_body):
        return len(list(OrderedDict.fromkeys([str(point["x"]) + str(point["y"]) for point in my_body])))
