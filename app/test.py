from game import Game
import networkx as nx

move333 = {"you": {"name": "jah-snake", "shout": "", "id": "gs_CxDGwmPtHHkrf6QGdfdc73cH", "health": 83, "body": [{"x": 6, "y": 5}, {"x": 6, "y": 6}, {"x": 5, "y": 6}, {"x": 5, "y": 7}, {"x": 4, "y": 7}, {"x": 4, "y": 8}, {"x": 3, "y": 8}, {"x": 3, "y": 7}, {"x": 2, "y": 7}, {"x": 2, "y": 6}, {"x": 2, "y": 5}, {"x": 2, "y": 4}, {"x": 2, "y": 3}, {"x": 2, "y": 2}, {"x": 1, "y": 2}, {"x": 1, "y": 3}, {"x": 1, "y": 4}, {"x": 1, "y": 5}, {"x": 1, "y": 6}, {"x": 1, "y": 7}, {"x": 1, "y": 8}, {"x": 1, "y": 9}, {"x": 1, "y": 10}, {"x": 2, "y": 10}, {"x": 3, "y": 10}, {"x": 4, "y": 10}, {"x": 5, "y": 10}, {"x": 5, "y": 9}, {"x": 5, "y": 8}, {"x": 6, "y": 8}, {"x": 7, "y": 8}, {"x": 7, "y": 7}, {"x": 7, "y": 6}, {"x": 7, "y": 5}, {"x": 8, "y": 5}, {"x": 8, "y": 6}, {"x": 8, "y": 7}, {"x": 8, "y": 8}, {"x": 8, "y": 9}, {"x": 8, "y": 10}, {"x": 9, "y": 10}, {"x": 10, "y": 10}, {"x": 10, "y": 9}, {"x": 9, "y": 9}, {"x": 9, "y": 8}, {"x": 10, "y": 8}, {"x": 10, "y": 7}, {"x": 10, "y": 6}, {"x": 10, "y": 5}, {"x": 10, "y": 4}, {"x": 10, "y": 3}, {"x": 9, "y": 3}, {"x": 9, "y": 2}, {"x": 8, "y": 2}, {"x": 8, "y": 3}, {"x": 7, "y": 3}]}, "board": {"snakes": [{"name": "jah-snake", "shout": "", "id": "gs_CxDGwmPtHHkrf6QGdfdc73cH", "health": 83, "body": [{"x": 6, "y": 5}, {"x": 6, "y": 6}, {"x": 5, "y": 6}, {"x": 5, "y": 7}, {"x": 4, "y": 7}, {"x": 4, "y": 8}, {"x": 3, "y": 8}, {"x": 3, "y": 7}, {"x": 2, "y": 7}, {"x": 2, "y": 6}, {"x": 2, "y": 5}, {"x": 2, "y": 4}, {"x": 2, "y": 3}, {"x": 2, "y": 2}, {"x": 1, "y": 2}, {"x": 1, "y": 3}, {"x": 1, "y": 4}, {"x": 1, "y": 5}, {"x": 1, "y": 6}, {"x": 1, "y": 7}, {"x": 1, "y": 8}, {"x": 1, "y": 9}, {"x": 1, "y": 10}, {"x": 2, "y": 10}, {"x": 3, "y": 10}, {"x": 4, "y": 10}, {"x": 5, "y": 10}, {"x": 5, "y": 9}, {"x": 5, "y": 8}, {"x": 6, "y": 8}, {"x": 7, "y": 8}, {"x": 7, "y": 7}, {"x": 7, "y": 6}, {"x": 7, "y": 5}, {"x": 8, "y": 5}, {"x": 8, "y": 6}, {"x": 8, "y": 7}, {"x": 8, "y": 8}, {"x": 8, "y": 9}, {"x": 8, "y": 10}, {"x": 9, "y": 10}, {"x": 10, "y": 10}, {"x": 10, "y": 9}, {"x": 9, "y": 9}, {"x": 9, "y": 8}, {"x": 10, "y": 8}, {"x": 10, "y": 7}, {"x": 10, "y": 6}, {"x": 10, "y": 5}, {"x": 10, "y": 4}, {"x": 10, "y": 3}, {"x": 9, "y": 3}, {"x": 9, "y": 2}, {"x": 8, "y": 2}, {"x": 8, "y": 3}, {"x": 7, "y": 3}]}], "food": [{"x": 6, "y": 0}, {"x": 2, "y": 9}, {"x": 5, "y": 3}, {"x": 7, "y": 9}], "width": 11, "height": 11}, "turn": 333, "game": {"id": "933beadd-1912-4c71-8b59-b1241c7688f4"}}

game = Game(move333)
game.update_game(move333)

print game.get_move()
