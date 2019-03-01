import networkx as nx
from collections import OrderedDict


class Game:
    def __init__(self, game_data):
        self.board_height = game_data['board']['height']
        self.board_width = game_data['board']['width']
        self.health = 100
        self.head = ""
        self.tail = ""
        self.board = ""
        self.foods = []
        self.snakes = []
        self.my_length = 0

    def update_game(self, game_data):
        self.head = (game_data["you"]["body"][0]["x"], game_data["you"]["body"][0]["y"])
        self.tail = (game_data["you"]["body"][-1]["x"], game_data["you"]["body"][-1]["y"])
        self.my_length = self.get_my_length(game_data["you"]["body"])
        self.foods = [(food["x"], food["y"]) for food in game_data["board"]["food"]]
        self.update_snakes(game_data)
        self.update_board()
        self.health = game_data["you"]["health"]

    def update_snakes(self, game_data):
        for snake in game_data["board"]["snakes"]:
            self.snakes = [(point["x"], point["y"]) for point in snake["body"]]
        self.snakes = list(OrderedDict.fromkeys(self.snakes))
        self.snakes.remove((game_data["you"]["body"][0]["x"], game_data["you"]["body"][0]["y"]))
        if len(game_data["you"]["body"]) > 1 and len(self.snakes)>0:
            self.snakes.remove((game_data["you"]["body"][-1]["x"], game_data["you"]["body"][-1]["y"]))

    def update_board(self):
        self.board = nx.Graph()
        for y in range(self.board_height):
            for x in range(self.board_width):
                current_node = (x, y)
                if current_node in self.snakes:
                    continue
                self.board.add_node(current_node)
                self.add_edges(current_node)

    def add_edges(self, current_node):
        x = current_node[0]
        y = current_node[1]
        for node in [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]:
            if self.board.has_node(node) and ((current_node not in [self.head, self.tail]) or (node not in [self.head, self.tail])):
                self.board.add_edge(node, current_node)

    def print_board(self):
        nx.draw_networkx(self.board)

    def make_node(self, x, y):
        return str(x) + str(y)

    def get_move(self):
        if self.my_length == 1:
            return 'up'
        if self.health < 50:
            destination = self.get_food_destination()
        else:
            destination = nx.shortest_path(self.board, self.head, self.tail)[1]
        return self.get_direction(destination)

    def get_food_destination(self):
        shortest_food_path = [i for i in range(1000)]
        for food_path in [nx.shortest_path(self.board, self.head, food) for food in self.foods]:
            if len(food_path) < len(shortest_food_path):
                shortest_food_path = food_path
        return shortest_food_path[1]

    def get_direction(self, destination):
        if self.head[0] == destination[0]:
            if self.head[1] > destination[1]:
                return 'up'
            return 'down'
        if self.head[0] > destination[0]:
            return 'left'
        return 'right'

    def get_my_length(self, my_body):
        return len(list(OrderedDict.fromkeys([self.make_node(point["x"], point["y"]) for point in my_body])))
