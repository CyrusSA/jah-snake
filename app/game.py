import networkx as nx
from collections import OrderedDict

class Game:
    def __init__(self, game_data):
        self.board_height = game_data['board']['height']
        self.board_width = game_data['board']['width']
        self.id = game_data['you']['id']
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
        self.shout = ""
        self.health_threshold = 90 if self.game_data['turn'] < 30 else 60
        self.calc_just_ate()
        self.foods = [(food["x"], food["y"]) for food in self.game_data["board"]["food"]]
        self.update_snakes()
        self.no_tails_board = self.update_board(self.extend_and_return(self.snakes, self.tails()))
        self.enemy_tails_board = self.update_board(self.extend_and_return(self.snakes, [self.tail]))
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
                for node in self.adjacent_nodes((snake['body'][0]['x'], snake["body"][0]["y"])):
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

    def get_shout(self):
        return self.shout

    def get_move(self):
        try:
            if self.my_length == 1:
                return self.direction((self.board_width, self.board_height))

            strats = [self.food_destination, self.tail_destination, self.enemy_tail_destination, self.finesse_destination]

            for strat in strats:
                destination = strat()
                if destination:
                    self.shout += "Strat: {}".format(strat.__name__[:-(len('_destination'))])
                    return self.direction(destination)

            # Random direction (maybe safe, maybe not)
            self.shout = "Strat: Random move"
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
            if self.no_tails_board.has_node(food) and self.first_to_food(food):
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
                # we fit in connected component to food
                if len(nx.node_connected_component(self.connectivity_board, food_path[-1])) < self.my_length:
                    shortest_food_path = food_path
                    continue
                try:
                    # path from food to our tail
                    safe_board_my_tail = self.update_board(self.extend_and_return(self.extend_and_return(self.snakes, [self.head]), self.tails(True)))
                    if nx.shortest_path(safe_board_my_tail, food_path[-1], self.tail):
                        shortest_food_path = food_path
                        continue
                except nx.NetworkXNoPath:
                    pass
                # path to enemy tail from food
                for enemy_tail in self.tails(True):
                    try:
                        connectivity_board_enemy_tail = self.update_board(self.extend_and_return(self.snakes, [self.head, self.tail]))
                        if nx.shortest_path(connectivity_board_enemy_tail, food_path[-1], enemy_tail):
                            shortest_food_path = food_path
                    except nx.NetworkXNoPath:
                        pass
        if shortest_food_path:
            self.shout += 'food at {} '.format(shortest_food_path[-1])
            return shortest_food_path[1]
        else:
            return None


    # True if food in corners and adjacent to corners except on the diagonal
    def in_danger_zone(self, food):
        limits = [self.danger_zone_lower, self.danger_zone_upper]
        return food not in [(i,j) for i in limits for j in limits] and (
                (food[0] <= self.danger_zone_lower and food[1] <= self.danger_zone_lower)
                or (food[0] <= self.danger_zone_lower and food[1] >= self.danger_zone_upper)
                or (food[0] >= self.danger_zone_upper and food[1] <= self.danger_zone_lower)
                or (food[0] >= self.danger_zone_upper and food[1] >= self.danger_zone_upper))


    def tail_destination(self):
        my_tail_board = self.update_board(self.extend_and_return(self.snakes, self.tails(True)))
        try:
            tail_destination = nx.astar_path(my_tail_board, self.head, self.tail, self.astar_heuristic)[1]
        except nx.NetworkXNoPath:
            return None

        return self.tail_chase_detour(my_tail_board, tail_destination, self.tail, self.id)


    def enemy_tail_destination(self):
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
        all_adjacent_nodes = [self.adjacent_nodes((point['x'], point['y'])) for point in reversed(self.game_data['you']['body'][1:(-2 if self.just_ate[self.id] else -1)])]
        flattened_adjacent_nodes = [candidate for candidates in all_adjacent_nodes for candidate in candidates if candidate != self.head]
        for candidate in flattened_adjacent_nodes:
            if self.connectivity_board.has_node(candidate):
                try:
                    path = nx.shortest_path(self.no_tails_board, self.head, candidate)
                    candidate_index = (flattened_adjacent_nodes.index(candidate) / 4) + 1
                    component = nx.node_connected_component(self.connectivity_board, candidate)
                    if len(path) < candidate_index:
                        return self.kill_time_destination(component, path)
                    return path[1]
                except nx.NetworkXNoPath:
                    continue
        return None


    def kill_time_destination(self, component, path):
        component_profile_x = [[n, 0] for n in range(self.board_height)]
        component_profile_y = component_profile_x[:]

        for (x,y) in component:
            component_profile_x[x][1] += 1
            component_profile_y[y][1] += 1

        sort_key = lambda profile : profile[1]
        component_profile_x.sort(key=sort_key)
        component_profile_y.sort(key=sort_key)

        gradient = 0
        for i in range(self.board_height):
            if component_profile_x[i][1] > component_profile_y[i][1]:
                break
            elif component_profile_x[i][1] < component_profile_y[i][1]:
                gradient = 1
                break

        if gradient:
            potential_moves = ((self.head[0] + 1, self.head[1]), (self.head[0] - 1, self.head[1]))
        else:
            potential_moves = ((self.head[0], self.head[1] + 1), (self.head[0], self.head[1] - 1))

        for move in potential_moves:
            if self.is_valid_move(move):
                return move

        return path[1]


    # get a random step into free space
    def random_destination(self):
        for node in self.adjacent_nodes(self.head):
            if self.is_valid_move(node):
                return node
        # Give up
        x, y = self.head
        return x-1, y


    def is_valid_move(self, move):
        return 0 <= move[0] < self.board_width and 0<= move[1] < self.board_height and (
            {'x': move[0], 'y': move[1]} not in [body for bodies in [snake['body'] for snake in self.game_data['board']['snakes']] for body in bodies]
        )


    # Dont follow closely if target snake just ate
    def tail_chase_detour(self, board, tail_destination, tail, id):
        if self.just_ate[id] and tail_destination and tail_destination == tail:
            for path in nx.all_simple_paths(board, self.head, tail, 4):
                if len(path) > 2:
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
        new_snakes = snakes[:]
        new_snakes.extend(extension)
        return new_snakes


    def remove_and_return(self, snakes, nodes):
        new_snakes = snakes[:]
        for node in nodes:
            if node in new_snakes:
                new_snakes.remove(node)
        return new_snakes


    def calc_just_ate(self):
        for snake in self.game_data['board']['snakes']:
            self.just_ate[snake['id']] = (snake['health'] == 100 and self.game_data["turn"] > 0)


    def snake_length(self, snake):
        return len(list(OrderedDict.fromkeys([str(point["x"]) + str(point["y"]) for point in snake])))


    def adjacent_nodes(self, node):
        x, y = node
        return [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]


    def longest_snake(self):
        longest_snake = self.game_data["you"]
        for snake in self.game_data["board"]["snakes"]:
            if self.snake_length(snake["body"]) > self.snake_length(longest_snake["body"]):
                longest_snake = snake
        return longest_snake['id']

    def first_to_food(self, food):
        try:
            my_path_len = len(nx.shortest_path(self.no_tails_board, self.head, food))
        except nx.NetworkXNoPath:
            return False

        for snake in self.game_data['board']['snakes']:
            if snake['id'] != self.id:
                enemy_nodes = [(snake['body'][0]['x'], snake['body'][0]['y'])]
                for node in self.adjacent_nodes(enemy_nodes[0]):
                    if node not in [(point['x'], point['y']) for point in snake['body']]:
                        enemy_nodes.append(node)
                enemy_heads_board = self.update_board(self.remove_and_return(self.snakes, enemy_nodes))
                try:
                    if self.longest_snake() == self.id:
                        if len(nx.shortest_path(enemy_heads_board, enemy_nodes[0], food)) < my_path_len:
                            return False
                    else:
                        if len(nx.shortest_path(enemy_heads_board, enemy_nodes[0], food)) <= my_path_len:
                            return False
                except nx.NetworkXNoPath:
                    continue
        return True
