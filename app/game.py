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
        self.update_board(game_data)
        self.health = game_data["you"]["health"]
        self.head = game_data["you"]["body"][0]
        self.tail = game_data["you"]["body"][-1]
        self.foods = [food for food in game_data["food"]]

    def update_snakes(self, game_data):
        self.snakes = [me for me in game_data["you"]["body"][1:-1]]
        for snake in game_data["board"]["snakes"]:
            self.snakes.extend(snake["body"])

    def __update_board(self):
        self.board = nx.Graph()
        for x in range(self.board_width):
            for y in range(self.board_height):
                current_node = {"x": x, "y": y}
                if current_node in self.snakes:
                    continue
                self.board.add_node(current_node)
                self.add_edges(current_node)

    def __add_edges(self, current_node):
        x = current_node["x"]
        y = current_node["y"]
        for node in [{"x": x-1, "y": y}, {"x": x+1, "y": y}, {"x": x, "y": y-1}, {"x": x, "y": y+1}]:
            if self.board.has_node(node):
                self.board.add_edge(node, current_node)