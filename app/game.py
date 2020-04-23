import networkx as nx
from collections import OrderedDict
import traceback

class Game:
    def __init__(self, game_data):
        self.board_height = game_data['board']['height']
        self.board_width = game_data['board']['width']
        self.just_ate = {}
        self.kill_moves = []

        # Distance from center
        center = (self.board_width/2, self.board_height/2)
        self.astar_heuristic = lambda curr, target : sum([(node[0] - center[0]) ** 2 + (node[1] - center[1]) ** 2 for node in (curr, target)]) + (-100 if curr in self.kill_moves else 0)

        self.danger_zone_lower = 1
        self.danger_zone_upper = 9
        

    # Updates game state with data from /move request.
    def update_game(self, game_data):
        self.game_data = game_data
        self.id = game_data['you']['id']
        self.head = (self.game_data["you"]["body"][0]["x"], self.game_data["you"]["body"][0]["y"])
        self.tail = (self.game_data["you"]["body"][-1]["x"], self.game_data["you"]["body"][-1]["y"])
        self.my_length = self.snake_length(self.game_data["you"]["body"])
        self.health = self.game_data["you"]["health"]
        self.shout = ""
        self.health_threshold = 99 if self.game_data['turn'] < 30 else 60
        self.calc_just_ate()
        self.foods = [(food["x"], food["y"]) for food in self.game_data["board"]["food"]]
        self.update_snakes()
        self.safety_nodes_longer = self.return_safety_nodes(True)
        self.safety_nodes_all = self.return_safety_nodes(False)
        self.no_tails_board = self.update_board(self.extend_and_return(self.snakes, self.tails()))
        self.connectivity_board = self.update_board(self.extend_and_return(self.snakes, [self.head]+self.tails()))
        self.kill_moves = self.cut_off_destinations()


    # Populate self.snakes with snake data, no tails.
    # If turn 0, don't add any of me
    # Else don't add my head
    def update_snakes(self):
        self.snakes = []
        for snake in self.game_data["board"]["snakes"]:
            # Add all snakes except us to self.snakes
            if snake["id"] != self.id:
                self.snakes.extend([(point["x"], point["y"]) for point in snake["body"][:(-2 if self.just_ate[snake['id']] else -1)]])
        # First turns edge case
        if self.game_data["turn"] == 0 or self.game_data["turn"] == 1:
            return
        # Add ourselves to self.snakes except head and tail
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
                return self.direction((self.board_width/2, self.board_height/2))

            strats_early_game = [self.food_destination, self.enemy_tail_destination, self.tail_destination, self.finesse_destination]
            strats = [self.food_destination, self.tail_destination, self.enemy_tail_destination, self.finesse_destination]

            early_game = len(self.game_data['board']['snakes']) >= 4 or self.game_data['turn'] < 50

            # Try strats in order with safety nodes
            for i in range(2):
                for strat in (strats_early_game if early_game else strats):
                    destination = strat()
                    if destination:
                        self.shout += "Strat: {}".format(strat.__name__[:-(len('_destination'))])
                        return self.direction(destination)

                # generate boards without safety nodes
                if i == 0:
                    self.safety_nodes_all = self.safety_nodes_longer = []
                    self.no_tails_board = self.update_board(self.extend_and_return(self.snakes, self.tails()))
                    self.connectivity_board = self.update_board(
                    self.extend_and_return(self.snakes, [self.head] + self.tails()))

            # Random direction (maybe safe, maybe not)
            self.shout = "Strat: Random move"
            return self.direction(self.random_destination())
        except Exception as e: # Unknown Exception, uh oh
            self.shout = 'Unknown Error: {}'.format(e)
            print traceback.format_exc()
            return self.direction(self.random_destination())


    # Return next moves that cut off enemy snakes
    def cut_off_destinations(self):
        if self.my_length==1:
            return []
        next_moves = [node for node in self.adjacent_nodes(self.head) if node not in self.snakes and node in self.connectivity_board]
        kill_moves = []
        # list of tuples (snake head, snake length) of enemy snakes
        enemy_snakes = [((snake['body'][0]['x'], snake['body'][0]['y']), self.snake_length(snake['body'])) for snake in self.game_data['board']['snakes'] if snake['id'] != self.id]
        for move in next_moves:
            board = self.update_board(self.extend_and_return(self.remove_and_return(self.snakes, [head for head, length in enemy_snakes]), [self.head, move]))
            for head, length in enemy_snakes:
                if len(nx.node_connected_component(board, head)) < length:
                    kill_moves.append(move)
        return kill_moves


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

        tails_connectivity_board = self.update_board(self.extend_and_return(self.snakes, [self.head], safety=True, longer_only=False))
        for food_path in paths:
            if len(self.foods) < len(self.game_data['board']['snakes']) and not self.first_to_food(food_path):
                continue
            if (len(food_path) < len(shortest_food_path) or len(shortest_food_path) == 0) and food_path[-1] in tails_connectivity_board:
                food_connected_component = nx.node_connected_component(tails_connectivity_board, food_path[-1])
                for tail in self.tails():
                    if tail in food_connected_component:
                        shortest_food_path = food_path

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
        if self.tail in my_tail_board:
            try:
                tail_destination = nx.astar_path(my_tail_board, self.head, self.tail, self.astar_heuristic)[1]
                return self.tail_chase_detour(my_tail_board, tail_destination, self.tail, self.just_ate[self.id])
            except nx.NetworkXNoPath:
                pass
        return None


    def enemy_tail_destination(self):
        enemy_tails_board = self.update_board(self.extend_and_return(self.snakes, [self.tail]))
        # remove tail with no path
        enemy_tail_paths = []
        for tail in self.tails(True):
            if not enemy_tails_board.has_node(tail):
                continue
            try:
                enemy_tail_paths.append(nx.astar_path(enemy_tails_board, self.head, tail, self.astar_heuristic))
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
        return self.tail_chase_detour(enemy_tails_board, shortest_path[1], shortest_path[-1])


    def finesse_destination(self):
        all_adjacent_nodes = [self.adjacent_nodes((point['x'], point['y'])) for point in reversed(self.game_data['you']['body'][1:(-2 if self.just_ate[self.id] else -1)])]
        flattened_adjacent_nodes = [candidate for candidates in all_adjacent_nodes for candidate in candidates if candidate != self.head]
        for candidate in flattened_adjacent_nodes:
            if self.connectivity_board.has_node(candidate):
                try:
                    path = nx.shortest_path(self.no_tails_board, self.head, candidate)
                    candidate_index = (flattened_adjacent_nodes.index(candidate) / 4) + 1
                    component = nx.node_connected_component(self.connectivity_board, candidate)
                    if len(component) < candidate_index:
                        continue
                    if len(path) - 1 < candidate_index:
                        return self.kill_time_destination(component, path, candidate_index)
                    return path[1]
                except nx.NetworkXNoPath:
                    continue
        return None


    def kill_time_destination(self, component, path, candidate_index):
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
            if self.is_valid_move(move) and self.connectivity_board.has_node(move) and len(nx.node_connected_component(self.connectivity_board, move)) >= candidate_index:
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


    # Dont follow closely if condition is true
    def tail_chase_detour(self, board, tail_destination, tail, condition=True):
        if condition and tail_destination and tail_destination == tail:
            for path in nx.all_simple_paths(board, self.head, tail, 4):
                if len(path) > 2:
                    tail_destination = path[1]
                    break
            # Have eaten for sure, will die if continue chasing tail
            if tail_destination == tail and tail == self.tail:
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


    # add nodes to a copy of snakes and return it
    def extend_and_return(self, snakes, extension, safety=True, longer_only=True):
        snakes_copy = snakes[:]
        snakes_copy.extend(extension)
        if safety:
            if longer_only:
                snakes_copy.extend(self.safety_nodes_longer)
            else:
                snakes_copy.extend(self.safety_nodes_all)
        return snakes_copy


    def remove_and_return(self, snakes, nodes):
        snakes_copy = snakes[:]
        for node in nodes:
            if node in snakes_copy:
                snakes_copy.remove(node)
        return snakes_copy


    def calc_just_ate(self):
        for snake in self.game_data['board']['snakes']:
            self.just_ate[snake['id']] = (snake['health'] == 100 and self.game_data["turn"] > 0)


    def snake_length(self, snake):
        return len(list(OrderedDict.fromkeys([str(point["x"]) + str(point["y"]) for point in snake])))


    def adjacent_nodes(self, node):
        x, y = node
        return [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]

    # Return true if we are closest to food
    def first_to_food(self, path):
        for snake in [snake for snake in self.game_data['board']['snakes'] if snake['id'] != self.id]:
            enemy_head = (snake['body'][0]['x'], snake['body'][0]['y'])
            enemy_heads_board = self.update_board(self.remove_and_return(self.snakes, [enemy_head]))
            try:
                if len(nx.shortest_path(enemy_heads_board, enemy_head, path[-1])) <= len(path) and len(snake['body']) > len(self.game_data['you']['body']):
                    return False
            except nx.NetworkXNoPath:
                continue
        return True


    # Return a list of nodes adjacent to the heads of enemy snakes
    def return_safety_nodes(self, longer_only):
        safety_nodes = []
        for snake in self.game_data['board']['snakes']:
            if snake['id'] != self.id:
                head = (snake['body'][0]['x'], snake["body"][0]["y"])
                edge_snake = self.is_edge_point(head)
                for node in self.adjacent_nodes(head):
                    if node not in self.snakes and node not in [self.head] and ((len(snake["body"]) >= self.my_length or not longer_only) or edge_snake):
                        safety_nodes.append(node)
        return safety_nodes

    def is_edge_point(self, head):
        x,y = head
        helper = lambda x,y : (x == self.danger_zone_upper or x == self.danger_zone_lower) and self.danger_zone_lower <= y <= self.danger_zone_upper
        return helper(x,y) and helper(y,x)
