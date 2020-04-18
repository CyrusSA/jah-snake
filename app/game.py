import networkx as nx
from collections import OrderedDict

class Game:
    def __init__(self, game_data):
        self.board_height = game_data['board']['height']
        self.board_width = game_data['board']['width']
        self.id = game_data['you']['id']
        self.shout = game_data['you']['shout']
        self.just_ate = {}

        # Distance from center
        center = (self.board_width/2, self.board_height/2)
        self.astar_heuristic = lambda n1, n2 : sum([(node[0] - center[0]) ** 2 + (node[1] - center[1]) ** 2 for node in (n1, n2)])

        self.danger_zone_lower = 1
        self.danger_zone_upper = 9

    # Updates game state with data from /move request.
    def update_game(self, game_data):
        self.game_data = game_data
        self.head = (self.game_data["you"]["body"][0]["x"], self.game_data["you"]["body"][0]["y"])
        self.tail = (self.game_data["you"]["body"][-1]["x"], self.game_data["you"]["body"][-1]["y"])
        self.my_length = self.snake_length(self.game_data["you"]["body"])
        self.health = self.game_data["you"]["health"]
        self.health_threshold = 100 if self.game_data['turn'] < 30 else 60
        self.calc_just_ate()
        self.foods = [(food["x"], food["y"]) for food in self.game_data["board"]["food"]]
        self.update_snakes()
        self.no_tails_board = self.update_board(self.extend_and_return(self.snakes, self.tails()))
        self.connectivity_board = self.update_board(self.extend_and_return(self.extend_and_return(self.snakes, [self.head]), self.tails()))


    # Populate self.snakes with snake data, no tails.
    # If turn 0, don't add any of me
    # Else don't add my head
    def update_snakes(self):
        self.snakes = []
        for snake in self.game_data["board"]["snakes"]:
            # Add all snakes except me to self.snakes
            if snake["id"] != self.game_data["you"]["id"]:
                self.snakes.extend([(point["x"], point["y"]) for point in snake["body"][:(-2 if self.just_ate[snake['id']] else -1)]])
                x = snake["body"][0]["x"]
                y = snake["body"][0]["y"]
                for node in self.adjacent_nodes(x, y):
                    if node not in self.snakes and node not in [self.head, self.tail] and len(snake["body"]) >= self.my_length:
                        self.snakes.append(node)

        if self.game_data["turn"] == 0 or self.game_data["turn"] == 1:
            return
        self.snakes.extend([(point["x"], point["y"]) for point in self.game_data["you"]["body"][1:(-2 if self.just_ate[self.id] else -1)] if point not in self.snakes])


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
                if self.my_length == 2:
                    if (current_node not in [self.head, self.tail]) or (node not in [self.head, self.tail]):
                        board.add_edge(node, current_node)
                else:
                    board.add_edge(node, current_node)


    def get_move(self):
        try:
            if self.my_length == 1:
                return self.direction((self.board_width, self.board_height))

            strats = [self.food_destination, self.tail_destination, self.enemy_tail_destination, self.finesse_destination]

            for strat in strats:
                destination = strat()
                if destination:
                    self.shout = "STRAT:", strat.__name__[:-(len('_destination'))]
                    return self.direction(destination)

            # Random direction (maybe safe, maybe not)
            self.shout = "STRAT: Random move"
            return self.direction(self.random_destination())
        except Exception as e: # Unknown Exception, uh oh
            self.shout = 'Unknown Error: {}'.format(e)
            return self.direction(self.random_destination())


    # Gets destination of closest food item
    def food_destination(self, force = False):
        shortest_food_path = []
        paths = []
        # get shortest path to each food on no_tails_board
        for food in self.foods:
            if self.in_danger_zone(food) and self.health > self.health_threshold and not force:
                continue
            if self.no_tails_board.has_node(food):
                try:
                    if self.game_data['turn'] < 30:
                        paths.append(nx.shortest_path(self.no_tails_board, self.head, food))
                    else:
                        paths.append(nx.astar_path(self.no_tails_board, self.head, food, self.astar_heuristic))
                except nx.NetworkXNoPath:
                    continue

        # get and return shortest path to food with a path back to tail, look ahead 1 turn
        for food_path in paths:
            if len(food_path) < len(shortest_food_path) or len(shortest_food_path) == 0:
                if len(nx.node_connected_component(self.connectivity_board, food_path[-1])) > self.my_length:
                    shortest_food_path = food_path
        return shortest_food_path[1] if shortest_food_path else None


    # True if food in corners and adjacent to corners except on the diagonal
    def in_danger_zone(self, food):
        limits = [self.danger_zone_lower, self.danger_zone_upper]
        return food not in [(i,j) for i in limits for j in limits] and (
                (food[0] <= self.danger_zone_lower and food[1] <= self.danger_zone_lower)
                or (food[0] <= self.danger_zone_lower and food[1] >= self.danger_zone_upper)
                or (food[0] >= self.danger_zone_upper and food[1] <= self.danger_zone_lower)
                or (food[0] >= self.danger_zone_upper and food[1] >= self.danger_zone_upper))


    def tail_destination(self):
        self.my_tail_board = self.update_board(self.extend_and_return(self.snakes, self.tails(True)))
        try:
            tail_destination = nx.astar_path(self.my_tail_board, self.head, self.tail, self.astar_heuristic)[1]
        except nx.NetworkXNoPath:
            return None

        return self.tail_chase_detour(self.my_tail_board, tail_destination, self.tail, self.id)


    def enemy_tail_destination(self):
        self.enemy_tails_board = self.update_board(self.extend_and_return(self.snakes, [self.tail]))
        # remove tail with no path
        enemy_tail_paths = []
        for tail in self.tails(True):
            if not self.enemy_tails_board.has_node(tail):
                continue
            try:
                enemy_tail_paths.append(nx.astar_path(self.enemy_tails_board, self.head, tail, self.astar_heuristic))
            except nx.NetworkXNoPath:
                pass
        # find and return shortest path
        shortest_path = []
        if enemy_tail_paths:
            shortest_path = enemy_tail_paths[0]
            for path in enemy_tail_paths:
                if len(path) < len(shortest_path):
                    shortest_path = path
        if not shortest_path:
            return None
        enemy_id = [snake for snake in self.game_data['board']['snakes'] if snake['body'][-1]['x'] == shortest_path[-1][0] and snake['body'][-1]['y'] == shortest_path[-1][1]][0]['id']
        return self.tail_chase_detour(self.enemy_tails_board, shortest_path[1], shortest_path[-1], enemy_id)


    def finesse_destination(self):
        all_adjacent_nodes = [self.adjacent_nodes(point['x'], point['y']) for point in reversed(self.game_data['you']['body'][1:(-2 if self.just_ate[self.id] else -1)])]
        flattened_adjacent_nodes = [candidate for candidates in all_adjacent_nodes for candidate in candidates if candidate != self.head]
        for candidate in flattened_adjacent_nodes:
            if self.connectivity_board.has_node(candidate):
                try:
                    nx.shortest_path(self.no_tails_board, self.head, candidate)
                    component = nx.node_connected_component(self.connectivity_board, candidate)
                    candidate_index = (flattened_adjacent_nodes.index(candidate) / 4) + 1
                    for path in nx.shortest_simple_paths(self.no_tails_board, self.head, candidate):
                        desired_path_len = candidate_index + len([food for food in self.foods if food in path]) + 2
                        if len(path) >= desired_path_len or len(path) == len(component) + 1:
                            return path[1]
                except nx.NetworkXNoPath:
                    continue
        return None


    # get a random step into free space
    def random_destination(self):
        self.my_length = 99
        self.update_snakes()
        random_move_board = self.update_board(self.extend_and_return(self.snakes, self.tails()))
        (x, y) = self.head
        for node in self.adjacent_nodes(x, y):
            if random_move_board.has_node(node):
                return node
        # Give up
        return (x - 1, y)


    # Dont follow closely if target snake just ate
    def tail_chase_detour(self, board, tail_destination, tail, id):
        if self.just_ate[id] and tail_destination and tail_destination == tail:
            for path in nx.all_simple_paths(board, self.head, tail, 4):
                if len(path) > 3:
                    tail_destination = path[1]
                    break
            if tail_destination == tail:
                return None

        return tail_destination


    def tails(self, enemy_only=False):
        tails = []
        # add the last body point of every snake except me to tails
        for snake in self.game_data["board"]["snakes"]:
            if snake["id"] == self.game_data["you"]["id"] and enemy_only:
                continue
            tails.append((snake["body"][-1]["x"], snake["body"][-1]["y"]))
        return tails


    # Returns direction to turn in order to reach destination
    def direction(self, destination):
        if self.head[0] == destination[0]:
            if self.head[1] > destination[1]:
                return 'up'
            return 'down'
        if self.head[0] > destination[0]:
            return 'left'
        return 'right'


    def extend_and_return(self, snakes, extension):
        new_list = snakes[:]
        new_list.extend(extension)
        return new_list


    def calc_just_ate(self):
        for snake in self.game_data['board']['snakes']:
            self.just_ate[snake['id']] = (snake['health'] == 100 and self.game_data["turn"] > 0)


    def snake_length(self, snake):
        return len(list(OrderedDict.fromkeys([str(point["x"]) + str(point["y"]) for point in snake])))


    def adjacent_nodes(self, x, y):
        return [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]


    def longest_snake(self):
        longest_snake = self.game_data["you"]
        for snake in self.game_data["board"]["snakes"]:
            if self.snake_length(snake["body"]) > self.snake_length(longest_snake["body"]):
                longest_snake = snake
        return longest_snake