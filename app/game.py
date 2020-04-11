import networkx as nx
from collections import OrderedDict
import random
import math

'''To-do
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
        self.health_threshold = 99
        self.just_ate = {}
        self.game_data = {}
        self.longest_snake = False
        self.astar_heuristic = lambda node, unneeded : math.sqrt(sum([(a - b) ** 2 for a, b in zip(node, (5,5))]))
        self.kill = 0

    # Updates game state with data from /move request.
    def update_game(self, game_data):
        self.game_data = game_data
        self.head = (self.game_data["you"]["body"][0]["x"], self.game_data["you"]["body"][0]["y"])
        self.tail = (self.game_data["you"]["body"][-1]["x"], self.game_data["you"]["body"][-1]["y"])
        self.my_length = self.get_snake_length(self.game_data["you"]["body"])
        self.health = self.game_data["you"]["health"]
        self.calc_just_ate()
        self.foods = [(food["x"], food["y"]) for food in self.game_data["board"]["food"]]
        self.update_snakes()
        self.no_tails_board = self.update_board(self.extend_and_return_snakes(self.get_tails()))
        self.my_tail_board = self.update_board(self.extend_and_return_snakes(self.get_tails(True)))
        self.enemy_tails_board = self.update_board(self.extend_and_return_snakes([self.tail]))
        self.longest_snake = bool([snake for snake in self.game_data["board"]["snakes"] if snake["id"] != self.game_data["you"]["id"]
                                   and self.get_snake_length(snake["body"]) < self.my_length])

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
                for node in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
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
                if self.my_length == 2 :
                    if (current_node not in [self.head, self.tail]) or (node not in [self.head, self.tail]):
                        board.add_edge(node, current_node)
                else:
                    board.add_edge(node, current_node)

    # Returns direction to turn. If health is below threshold, move will be towards closest food item.
    # Else if turn 0, return default move
    # Else move towards tail
    def get_move(self):
        try:
            if self.my_length == 1 or self.kill:
                print 'killed'
                return 'up'

            # Check food case first
            food_destination = self.get_food_destination()
            if self.health < self.health_threshold or not self.longest_snake:
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
            if food_destination:
                print "Getting food after force checking"
                return self.get_direction(food_destination)

            # Random direction (maybe safe, maybe not)
            print "Random move, no errors"
            return self.get_direction(self.get_random_destination())
        except Exception as e: # Unknown Exception, uh oh
            print 'Unknown Error: {}'.format(e)
            self.kill = 1
            return self.get_direction(self.get_random_destination())

    # Gets destination of closest food item
    def get_food_destination(self):
        shortest_food_path = []
        paths = []
        # get shortest path to each food on no_tails_board
        for food in self.foods:
            if self.no_tails_board.has_node(food):
                try:
                    paths.append(nx.astar_path(self.no_tails_board, self.head, food, self.astar_heuristic))
                except nx.NetworkXNoPath:
                    continue

        # get and return shortest path to food with a path back to tail, look ahead 1 turn
        for food_path in paths:
            if len(food_path) < len(shortest_food_path) or len(shortest_food_path) == 0:
                try:
                    future_board = self.update_board(self.extend_and_return_snakes([food_path[0]]))  # board with head cell filled and including all tails
                    nx.shortest_path(future_board, food_path[-1], self.tail)
                except nx.NetworkXNoPath:
                    print "Avoided cornering!!"
                    continue
                shortest_food_path = food_path
        return shortest_food_path[1] if shortest_food_path else None

    def get_tail_destination(self):
        try:
            tail_destination = nx.astar_path(self.my_tail_board, self.head, self.tail, self.astar_heuristic)[1]
        except nx.NetworkXNoPath:
            return None

        # Two body points stacked at tail, don't follow closely
        if self.just_ate[self.id] and tail_destination and tail_destination == self.tail:
            for path in nx.all_simple_paths(self.my_tail_board, self.head, self.tail, 4):
                if len(path) > 3:
                    tail_destination = path[1]
                    break
            if tail_destination == self.tail:
                print "No alternate paths"

        return tail_destination

    # get path to closest enemy tail
    def get_enemy_tail_destination(self):
        # remove tail with no path
        enemy_tail_paths = []
        for tail in self.get_tails(True):
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
        return shortest_path[1] if shortest_path else None

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

    def extend_and_return_snakes(self, extension):
        new_list = self.snakes[:]
        new_list.extend(extension)
        return new_list

    # get a random step into free space
    def get_random_destination(self):
        (x, y) = self.head
        adjacent_nodes = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        for node in adjacent_nodes:
            if self.no_tails_board.has_node(node):
                return node
        # Give up
        return (x - 1, y)

    def calc_just_ate(self):
        for snake in self.game_data['board']['snakes']:
            self.just_ate[snake['id']] = (snake['health'] == 100 and self.game_data["turn"] > 0)

    def get_snake_length(self, snake):
        return len(list(OrderedDict.fromkeys([str(point["x"]) + str(point["y"]) for point in snake])))

    # def pathfind(self, board, source, dest):
    #     me = self.game_data['you']
    #     enemies = sorted([snake['body'] for snake in self.game_data['board']['snakes'] if snake['id'] != me['id']], key = lambda body : math.fabs(body[0]['x'] - self.head[0]) + math.fabs(body[0]['y'] - self.head[1]))
    #



#     def get_snake_gradient(self, snake):
#     	offset = 

# class Gradient:
# 	def __init__(self, snake):
