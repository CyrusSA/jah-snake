import networkx as nx
from collections import OrderedDict
import traceback


class Game:
    def __init__(self, game_data):
        self.board_height = game_data['board']['height']
        self.board_width = game_data['board']['width']
        self.just_ate = {}
        self.kill_moves = []
        self.shout = ''
        self.health_threshold = 60

        # Distance from center
        center = (self.board_width / 2, self.board_height / 2)
        self.astar_heuristic = lambda curr, target: sum([(node[0] - center[0]) ** 2 + (node[1] - center[1]) ** 2 for node in (curr, target)])

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
        self.calc_just_ate()
        self.set_health_thresh()
        self.foods = [(food["x"], food["y"]) for food in self.game_data["board"]["food"]]
        self.update_snakes()
        self.danger_nodes_longer_only = self.danger_nodes(longer_only=True)
        self.danger_nodes_all = self.danger_nodes(longer_only=False)
        self.update_global_boards()

    def set_health_thresh(self):
        self.health_threshold = 60
        my_len = len(self.game_data['you']['body'])
        for snake in self.game_data['board']['snakes']:
            if snake['id'] != self.id and len(snake['body']) < my_len + 1:
                self.health_threshold = 101

    def calc_just_ate(self):
        for snake in self.game_data['board']['snakes']:
            self.just_ate[snake['id']] = (snake['health'] == 100 and self.game_data["turn"] > 0)

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
        self.snakes.extend([(point["x"], point["y"]) for point in self.game_data["you"]["body"][1:(-2 if self.just_ate[self.id] else -1)] if
                            point not in self.snakes])

    # add nodes to a copy of snakes and return it
    def extend_and_return(self, snakes, extension, safety=True, longer_only=True):
        snakes_copy = snakes[:]
        snakes_copy.extend(extension)
        if safety:
            if longer_only:
                snakes_copy.extend(self.danger_nodes_longer_only)
            else:
                snakes_copy.extend(self.danger_nodes_all)
        return snakes_copy

    def remove_and_return(self, snakes, nodes):
        snakes_copy = snakes[:]
        for node in nodes:
            if node in snakes_copy:
                snakes_copy.remove(node)
        return snakes_copy

    def snake_length(self, snake):
        return len(list(OrderedDict.fromkeys([str(point["x"]) + str(point["y"]) for point in snake])))

    def tails(self, enemy_only=False):
        tails = []
        # add the last body point of every snake except me to tails
        for snake in self.game_data["board"]["snakes"]:
            if snake["id"] == self.game_data["you"]["id"] and enemy_only:
                continue
            tails.append((snake["body"][-1]["x"], snake["body"][-1]["y"]))
        return tails

    def adjacent_nodes(self, node, valid_moves_only=True):
        x, y = node
        return [node for node in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)] if ((not valid_moves_only) or self.is_valid_move(node))]

    def update_global_boards(self):
        self.no_tails_board = self.create_board(self.extend_and_return(self.snakes, self.tails()))
        self.connectivity_board = self.create_board(self.extend_and_return(self.snakes, [self.head] + self.tails()))

    # Creates and populates graph of board points. Does not add a point if it houses a snake.
    def create_board(self, snakes):
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
                foods = sorted(self.foods, key=lambda food: (food[0] - self.head[0]) ** 2 + (food[1] - self.head[1]) ** 2)
                self.shout = "STRAT: Initial move"
                return self.direction(foods[0])

            strats = [self.food_destination, self.tail_destination, self.enemy_tail_destination, self.finesse_destination]

            cutoff_nodes = self.cutoff_nodes()

            for i in range(2):
                # Try strats in order with safety nodes
                for strat in strats:
                    path = strat()
                    if path:
                        cutoff_maneuver = self.cutoff_maneuver(path) if cutoff_nodes else []
                        if cutoff_maneuver:
                            self.shout += "Strat: {}, Cutoff {}".format(strat.__name__[:-(len('_destination'))],
                                                                        cutoff_maneuver[1:-1])
                            return self.direction(cutoff_maneuver[1])
                        self.shout += "Strat: {}".format(strat.__name__[:-(len('_destination'))])
                        return self.direction(path[1])

                # generate boards without safety nodes
                self.danger_nodes_all = self.danger_nodes_longer_only = self.danger_nodes(True, desperate=True)
                self.update_global_boards()

            # Random direction (maybe safe, maybe not)
            self.shout = "Strat: Random move"
            return self.direction(self.random_destination())
        except Exception as e:  # Unknown Exception, uh oh
            self.shout = 'Unknown Error: {}'.format(e)
            print traceback.format_exc()
            return self.direction(self.random_destination())

    # Gets destination of closest food item
    def food_destination(self):
        shortest_food_path = []
        paths = []
        # get shortest path to each food on no_tails_board
        for food in self.foods:
            if self.is_in_danger_zone(food) and self.health > self.health_threshold:
                continue
            if self.no_tails_board.has_node(food):
                try:
                    if self.game_data['turn'] < 30:
                        paths.append(nx.shortest_path(self.no_tails_board, self.head, food))
                    else:
                        paths.append(nx.astar_path(self.no_tails_board, self.head, food, self.astar_heuristic))
                except nx.NetworkXNoPath:
                    continue

        tails_connectivity_board = self.create_board(self.extend_and_return(self.snakes, [self.head], safety=True, longer_only=False))
        for food_path in paths:
            if (len(food_path) < len(shortest_food_path) or len(shortest_food_path) == 0) and food_path[-1] in tails_connectivity_board:
                food_connected_component = nx.node_connected_component(tails_connectivity_board, food_path[-1])
                for tail in self.tails():
                    if tail in food_connected_component:
                        shortest_food_path = food_path

        if shortest_food_path:
            self.shout += 'food at {} '.format(shortest_food_path[-1])
        return shortest_food_path

    def tail_destination(self):
        my_tail_board = self.create_board(self.extend_and_return(self.snakes, self.tails(True)))
        if self.tail in my_tail_board:
            try:
                path = nx.astar_path(my_tail_board, self.head, self.tail, self.astar_heuristic)
                return self.tail_chase_detour(my_tail_board, path, self.id)
            except nx.NetworkXNoPath:
                pass
        return None

    def enemy_tail_destination(self):
        enemy_tails_board = self.create_board(self.extend_and_return(self.snakes, [self.tail]))
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

        enemy_id = [snake for snake in self.game_data['board']['snakes'] if
                    snake['body'][-1]['x'] == shortest_path[-1][0] and snake['body'][-1]['y'] == shortest_path[-1][1]][0]['id']
        return self.tail_chase_detour(enemy_tails_board, shortest_path, enemy_id)

    def finesse_destination(self):
        all_adjacent_nodes = [self.adjacent_nodes((point['x'], point['y']), valid_moves_only=False) for point in
                              reversed(self.game_data['you']['body'][1:(-2 if self.just_ate[self.id] else -1)])]
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
                    return path
                except nx.NetworkXNoPath:
                    continue
        return None

    def kill_time_destination(self, component, path, candidate_index):
        component_profile_x = [[n, 0] for n in range(self.board_height)]
        component_profile_y = component_profile_x[:]

        for (x, y) in component:
            component_profile_x[x][1] += 1
            component_profile_y[y][1] += 1

        sort_key = lambda profile: profile[1]
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
            if self.is_valid_move(move) and self.connectivity_board.has_node(move) and len(
                    nx.node_connected_component(self.connectivity_board, move)) >= candidate_index:
                return [self.head, move]

        return path

    # get a random step into free space
    def random_destination(self):
        moves = self.adjacent_nodes(self.head)
        return moves[0] if moves else (self.head[0] - 1, self.head[1])

    # Returns direction to turn in order to reach destination
    def direction(self, destination):
        if self.head[0] == destination[0]:
            if self.head[1] > destination[1]:
                return 'up'
            return 'down'
        if self.head[0] > destination[0]:
            return 'left'
        return 'right'

    # Return next moves that cut off enemy snakes
    def cutoff_nodes(self):
        if self.my_length == 1:
            return []
        next_moves = [node for node in self.adjacent_nodes(self.head) if node not in self.snakes and node in self.connectivity_board]
        kill_moves = []
        # list of tuples (snake head, snake length) of enemy snakes
        enemy_snakes = [((snake['body'][0]['x'], snake['body'][0]['y']), len(snake['body'])) for snake in self.game_data['board']['snakes'] if
                        snake['id'] != self.id]
        for move in next_moves:
            current_board = self.create_board(
                self.extend_and_return(self.remove_and_return(self.snakes, [head for head, length in enemy_snakes]), [self.head], safety=False))
            cutoff_board = self.create_board(
                self.extend_and_return(self.remove_and_return(self.snakes, [head for head, length in enemy_snakes]), [self.head, move], safety=False))
            for head, length in enemy_snakes:
                if len(nx.node_connected_component(current_board, head)) < length:
                    # snake already cutoff
                    continue
                if len(nx.node_connected_component(cutoff_board, head)) < length:
                    kill_moves.append(move)
        return kill_moves

    # Return a list of nodes adjacent to the heads of enemy snakes
    def danger_nodes(self, longer_only, desperate=False):
        safety_nodes = []
        all_possibilities = {}

        my_adjacent_nodes = [node for node in self.adjacent_nodes(self.head) if self.is_valid_move(node)]

        for node in my_adjacent_nodes:
            all_possibilities[node] = [[], []]

        for snake in [snake for snake in self.game_data['board']['snakes'] if snake['id'] != self.id]:
            head = (snake['body'][0]['x'], snake["body"][0]["y"])
            is_longer = len(snake["body"]) >= len(self.game_data['you']['body'])
            is_unsafe = is_longer or not longer_only
            enemy_adjacent_nodes = [node for node in self.adjacent_nodes(head) if self.is_valid_move(node)]

            if is_longer:
                possibilities = [[x, y] for x in enemy_adjacent_nodes for y in
                                 [node for node in self.adjacent_nodes(self.head) if not (node == self.tail and self.my_length == 2)] if x != y]

                for possibility in possibilities:
                    board = self.create_board(self.extend_and_return(self.snakes, [self.head] + possibility, False))
                    next_move_set = [[node for node in nodes if board.has_node(node)] for nodes in
                                     [self.adjacent_nodes(possibility[0]), self.adjacent_nodes(possibility[1])]]
                    all_possibilities[possibility[1]][0].extend(next_move_set[0])
                    all_possibilities[possibility[1]][1] = next_move_set[1]

            for node in enemy_adjacent_nodes:
                edge_blocked = self.is_inner_edge_point(head) and self.is_outer_edge_point(node) and not desperate
                if self.is_valid_move(node) and node not in self.snakes and node not in [self.head] and (is_unsafe or edge_blocked):
                    safety_nodes.append(node)

        for node in my_adjacent_nodes:
            is_confrontation_node = all_possibilities.has_key(node) and all_possibilities[node][0] and all(
                x in all_possibilities[node][0] for x in all_possibilities[node][1])
            if not desperate and node not in safety_nodes and is_confrontation_node:
                safety_nodes.append(node)
        return safety_nodes

    def cutoff_maneuver(self, path):
        adjacent_nodes = [self.adjacent_nodes(node) for node in path]
        for i in range(len(adjacent_nodes)):
            for node in adjacent_nodes[i]:
                if node not in path and node in self.kill_moves and self.no_tails_board.has_node(node) and self.no_tails_board.has_node(path[i + 1]):
                    try:
                        for maneuver in nx.all_simple_paths(self.no_tails_board, path[i], path[i + 1], 6):
                            if node in maneuver:
                                return maneuver
                    except nx.NetworkXNoPath:
                        continue
        return None

    # Dont follow closely if target snake just ate
    def tail_chase_detour(self, board, tail_path, id):
        if not tail_path:
            return tail_path
        tail_destination, tail = tail_path[1], tail_path[-1]
        is_enemy_tail = tail != self.tail
        if (self.just_ate[id] or is_enemy_tail) and tail_destination and tail_destination == tail:
            for path in nx.all_simple_paths(board, self.head, tail, 4):
                if len(path) > 2:
                    return path
            if not is_enemy_tail:
                return None

        return tail_path

    def is_valid_move(self, move):
        if not (0 <= move[0] < self.board_width and 0 <= move[1] < self.board_height):
            return False

        for snake in self.game_data['board']['snakes']:
            tail_pos = -1
            if self.just_ate[snake['id']]:
                if move == (snake['body'][-1]['x'], snake['body'][-1]['y']):
                    return False
                tail_pos = -2
            if {'x': move[0], 'y': move[1]} in [body for bodies in
                                                [snake['body'][(0 if len(snake['body']) >= len(self.game_data['you']['body']) else 1):tail_pos] for
                                                 snake in self.game_data['board']['snakes']] for body in bodies]:
                return False

        return True

    # True if food in corners and adjacent to corners except on the diagonal
    def is_in_danger_zone(self, food):
        limits = [self.danger_zone_lower, self.danger_zone_upper]
        return food not in [(i, j) for i in limits for j in limits] and (
            (food[0] <= self.danger_zone_lower and food[1] <= self.danger_zone_lower)
            or (food[0] <= self.danger_zone_lower and food[1] >= self.danger_zone_upper)
            or (food[0] >= self.danger_zone_upper and food[1] <= self.danger_zone_lower)
            or (food[0] >= self.danger_zone_upper and food[1] >= self.danger_zone_upper))

    def is_inner_edge_point(self, head):
        x, y = head
        helper = lambda x, y: (x == self.danger_zone_upper or x == self.danger_zone_lower) and self.danger_zone_lower <= y <= self.danger_zone_upper
        return helper(x, y) or helper(y, x)

    def is_outer_edge_point(self, node):
        x, y = node
        helper = lambda x: x == 0 or x == self.board_height - 1
        return helper(x) or helper(y)
