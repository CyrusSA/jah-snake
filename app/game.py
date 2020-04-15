import networkx as nx
from collections import OrderedDict
import operator

'''To-do
- Edge case where enemy head is next to our tail
- Dont go for food unless path to tail - check ahead a step - DONEish - logic is weak rn, needs discussion
- Dont go for food if enemy can get there first unless low health or longer than enemy by a margin - DO LATER
- go to possible enemy next move only if longer than enemy
- If no paths, add enemy next moves to board
- Dont use board to find safe moves, defeats the purpose, use game data
- Edit food logic - discuss, turn threshold(turns, no of snakes), health threshold. Want to be longest? or nah
- Use simple paths to fill up board - discuss
'''

class Game:
    def __init__(self, game_data):
        self.board_height = game_data['board']['height']
        self.board_width = game_data['board']['width']
        self.health = 100
        self.head = ("", "")
        self.tail = ("", "")
        self.id = game_data['you']['id']
        self.no_tails_board = nx.Graph()
        self.my_tail_board = nx.Graph()
        self.enemy_tails_board = nx.Graph()
        self.foods = []
        self.snakes = []
        self.my_length = 0
        self.health_threshold = 0
        self.just_ate = {}
        self.game_data = {}
        self.astar_heuristic = lambda n1, n2 : sum([(node[0] - 5) ** 2 + (node[1] - 5) ** 2 for node in (n1, n2)])
        self.danger_zone_lower = 1
        self.danger_zone_upper = 9

    # Updates game state with data from /move request.
    def update_game(self, game_data):
        self.game_data = game_data
        self.head = (self.game_data["you"]["body"][0]["x"], self.game_data["you"]["body"][0]["y"])
        self.tail = (self.game_data["you"]["body"][-1]["x"], self.game_data["you"]["body"][-1]["y"])
        self.my_length = self.get_snake_length(self.game_data["you"]["body"])
        self.health = self.game_data["you"]["health"]
        self.health_threshold = 100 if self.game_data['turn'] < 30 else 60
        self.calc_just_ate()
        self.foods = [(food["x"], food["y"]) for food in self.game_data["board"]["food"]]
        self.update_snakes()
        self.no_tails_board = self.update_board(self.extend_and_return(self.snakes, self.get_tails()))
        self.my_tail_board = self.update_board(self.extend_and_return(self.snakes, self.get_tails(True)))
        self.enemy_tails_board = self.update_board(self.extend_and_return(self.snakes, [self.tail]))
        self.connectivity_board = self.update_board(self.extend_and_return(self.extend_and_return(self.snakes, [self.head]), self.get_tails()))

        #self.health_threshold = 99 if len(self.game_data['board']['snakes']) > 2 else 80

    # Populate self.snakes with snake data.
    # If turn 0, don't add any of me
    # If just ate, don't add tail
    # Else don't add my head and tail
    def update_snakes(self):
        self.snakes = []
        for snake in self.game_data["board"]["snakes"]:
            # Add all snakes except me to self.snakes
            if snake["id"] != self.game_data["you"]["id"]:
                self.snakes.extend([(point["x"], point["y"]) for point in snake["body"][:(-2 if self.just_ate[snake['id']] else -1)]])
                x = snake["body"][0]["x"]
                y = snake["body"][0]["y"]
                for node in self.get_adjacent_nodes(x, y):
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

    # Returns direction to turn. If health is below threshold, move will be towards closest food item.
    # Else if turn 0, return default move
    # Else move towards tail
    def get_move(self):
        try:
            if self.my_length == 1:
                return self.get_direction((self.board_width, self.board_height))

            # Check food case first
            food_destination = self.get_food_destination()
            if food_destination:
                print "Getting food"
                return self.get_direction(food_destination)

            # Then chase tail
            tail_destination = self.get_tail_destination()
            if tail_destination:
                print "Chasing tail"
                return self.get_direction(tail_destination)

            # else chase enemy tail
            enemy_tail_destination = self.get_enemy_tail_destination()
            if enemy_tail_destination:
                print "Chasing enemy tail"
                return self.get_direction(enemy_tail_destination)

            # If none of the above, force check food
            food_destination = self.get_food_destination(True)
            if food_destination:
                print "Getting food"
                return self.get_direction(food_destination)

            finesse_destination = self.get_finesse_destination()
            if finesse_destination:
                print "Finessing"
                return self.get_direction(finesse_destination)

            # Random direction (maybe safe, maybe not)
            print "Random move, no errors"
            return self.get_direction(self.get_random_destination())
        except Exception as e: # Unknown Exception, uh oh
            print 'Unknown Error: {}'.format(e)
            return self.get_direction(self.get_random_destination())

    # Gets destination of closest food item
    def get_food_destination(self, force = False):
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

                # shortest_enemy_path_len = 0
                # for snake in self.game_data['board']['snakes']:
                #     if snake['id'] == self.id or len(snake['body'] < self.my_length):
                #         continue
                #     try:
                #         path = nx.shortest_path(self.connectivity_board)

        # get and return shortest path to food with a path back to tail, look ahead 1 turn
        for food_path in paths:
            if len(food_path) < len(shortest_food_path) or len(shortest_food_path) == 0:
                if len(nx.node_connected_component(self.connectivity_board, food_path[-1])) > self.my_length:
                    shortest_food_path = food_path
        return shortest_food_path[1] if shortest_food_path else None

    def in_danger_zone(self, food):
        limits = [self.danger_zone_lower, self.danger_zone_upper]
        return food not in [(i,j) for i in limits for j in limits] and (
                (food[0] <= self.danger_zone_lower and food[1] <= self.danger_zone_lower)
                or (food[0] <= self.danger_zone_lower and food[1] >= self.danger_zone_upper)
                or (food[0] >= self.danger_zone_upper and food[1] <= self.danger_zone_lower)
                or (food[0] >= self.danger_zone_upper and food[1] >= self.danger_zone_upper))

    def get_tail_destination(self):
        try:
            tail_destination = nx.astar_path(self.my_tail_board, self.head, self.tail, self.astar_heuristic)[1]
        except nx.NetworkXNoPath:
            return None

        return self.tail_chase_detour(self.my_tail_board, tail_destination, self.tail, self.id)

    # get path to closest enemy tail
    def get_enemy_tail_destination(self):
        # remove tail with no path
        enemy_tail_paths = []
        for tail in self.get_tails(True):
            if not self.enemy_tails_board.has_node(tail):
                continue
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
        if not shortest_path:
            return None
        enemy_id = [snake for snake in self.game_data['board']['snakes'] if snake['body'][-1]['x'] == shortest_path[-1][0] and snake['body'][-1]['y'] == shortest_path[-1][1]][0]['id']
        return self.tail_chase_detour(self.enemy_tails_board, shortest_path[1], shortest_path[-1], enemy_id)

    def tail_chase_detour(self, board, tail_destination, tail, id):
        # Two body points stacked at tail, don't follow closely
        if self.just_ate[id] and tail_destination and tail_destination == tail:
            for path in nx.all_simple_paths(board, self.head, tail, 4):
                if len(path) > 3:
                    tail_destination = path[1]
                    break
            if tail_destination == tail:
                print "No alternate paths"
                return None

        return tail_destination

    def get_finesse_destination(self):
        all_adjacent_nodes = [self.get_adjacent_nodes(point['x'], point['y']) for point in reversed(self.game_data['you']['body'][1:(-2 if self.just_ate[self.id] else -1)])]
        for candidate in [candidate for candidates in all_adjacent_nodes for candidate in candidates if candidate != self.head]:
            if self.connectivity_board.has_node(candidate):
                try:
                    nx.shortest_path(self.no_tails_board, self.head, candidate)
                    for path in nx.shortest_simple_paths(self.no_tails_board, self.head, candidate):
                        if len(path) >= self.my_length or len(path) == len(nx.node_connected_component(self.connectivity_board, path[-1])) + 1:
                            return path[1]
                except nx.NetworkXNoPath:
                    continue
        return None


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

    def extend_and_return(self, snakes, extension):
        new_list = snakes[:]
        new_list.extend(extension)
        return new_list

    # get a random step into free space
    def get_random_destination(self):
        self.my_length = 99
        self.update_snakes()
        random_move_board = self.update_board(self.extend_and_return(self.snakes, self.get_tails()))
        (x, y) = self.head
        for node in self.get_adjacent_nodes(x,y):
            if random_move_board.has_node(node):
                return node
        # Give up
        print "give up"
        return (x - 1, y)

    def calc_just_ate(self):
        for snake in self.game_data['board']['snakes']:
            self.just_ate[snake['id']] = (snake['health'] == 100 and self.game_data["turn"] > 0)

    def get_snake_length(self, snake):
        return len(list(OrderedDict.fromkeys([str(point["x"]) + str(point["y"]) for point in snake])))

    # probably a way to do this with an in place sort
    def longest_snake(self):
        longest_snake = self.game_data["you"]
        for snake in self.game_data["board"]["snakes"]:
            if self.get_snake_length(snake["body"]) > self.get_snake_length(longest_snake["body"]):
                longest_snake = snake
        return longest_snake

    def get_adjacent_nodes(self, x, y):
        return [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]

