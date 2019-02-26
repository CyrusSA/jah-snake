import networkx as nx


class Game:
    def __init__(self, game_data):
        print "hello"
        self.board_height = game_data['board']['height']
        self.board_width = game_data['board']['width']
        self.health = 100
        self.head = ""
        self.tail = ""
        self.board = ""
        self.foods = []
        self.snakes = []

    def update_game(self, game_data):
        self.update_snakes(game_data)
        self.update_board()
        self.health = game_data["you"]["health"]
        self.head = Node(game_data["you"]["body"][0]["x"], game_data["you"]["body"][0]["y"])
        self.tail = Node(game_data["you"]["body"][-1]["x"], game_data["you"]["body"][-1]["y"])
        self.foods = [Node(food["x"], food["y"]) for food in game_data["board"]["food"]]

    def update_snakes(self, game_data):
        for snake in game_data["board"]["snakes"]:
            self.snakes = [Node(point["x"], point["y"]) for point in snake["body"]]
        self.snakes.remove(Node(game_data["you"]["body"][0]["x"], game_data["you"]["body"][0]["y"]))
        self.snakes.remove(Node(game_data["you"]["body"][-1]["x"], game_data["you"]["body"][-1]["y"]))

    def update_board(self):
        self.board = nx.Graph()
        for y in range(self.board_height):
            for x in range(self.board_width):
                current_node = Node(x, y)
                if current_node in self.snakes:
                    continue
                self.board.add_node(current_node.string())
                self.add_edges(current_node)

    def add_edges(self, current_node):
        x = current_node.x
        y = current_node.y
        for node in [Node(x-1, y), Node(x+1, y), Node(x, y-1), Node(x, y+1)]:
            if self.board.has_node(node.string()):
                self.board.add_edge(node.string(), current_node.string())

    def print_board(self):
        nx.draw_networkx(self.board)

    def get_node(self, node_string):
        return Node(int(node_string[0]), int(node_string[1]))

    def get_move(self):
        destination = nx.shortest_path(self.board, self.head.string(), self.tail.string())[0]
        return self.get_direction(self.get_node(destination))

    def get_direction(self, destination):
        if self.head.x == destination.x:
            if self.head.y > destination.y:
                return "down"
            return "up"
        if self.head.x > destination.x:
            return "left"
        return "right"


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def string(self):
        return str(self.x) + str(self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
