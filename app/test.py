from game import Game

move = {"you": {"name": "santino-marella", "id": "gs_J8SwvF3VqS4JjwxwrVJwSCPV", "shout": "food at (9, 3) Strat: food", "health": 96, "body": [{"y": 6, "x": 2}, {"y": 5, "x": 2}, {"y": 5, "x": 3}, {"y": 6, "x": 3}, {"y": 7, "x": 3}, {"y": 7, "x": 4}, {"y": 6, "x": 4}, {"y": 5, "x": 4}, {"y": 5, "x": 5}, {"y": 5, "x": 6}, {"y": 5, "x": 7}, {"y": 5, "x": 8}, {"y": 4, "x": 8}, {"y": 4, "x": 7}, {"y": 4, "x": 6}, {"y": 4, "x": 5}, {"y": 4, "x": 4}, {"y": 3, "x": 4}, {"y": 3, "x": 3}, {"y": 2, "x": 3}, {"y": 1, "x": 3}, {"y": 0, "x": 3}, {"y": 0, "x": 2}]}, "board": {"height": 11, "snakes": [{"name": "Sir Pent", "id": "gs_PPMFpBFCKhQQd3FGdC3WSrq4", "shout": "Duration: 6", "health": 79, "body": [{"y": 8, "x": 0}, {"y": 9, "x": 0}, {"y": 9, "x": 1}, {"y": 9, "x": 2}, {"y": 9, "x": 3}, {"y": 9, "x": 4}, {"y": 9, "x": 5}, {"y": 9, "x": 6}, {"y": 9, "x": 7}, {"y": 9, "x": 8}, {"y": 9, "x": 9}, {"y": 8, "x": 9}, {"y": 7, "x": 9}]}, {"name": "santino-marella", "id": "gs_J8SwvF3VqS4JjwxwrVJwSCPV", "shout": "food at (9, 3) Strat: food", "health": 96, "body": [{"y": 6, "x": 2}, {"y": 5, "x": 2}, {"y": 5, "x": 3}, {"y": 6, "x": 3}, {"y": 7, "x": 3}, {"y": 7, "x": 4}, {"y": 6, "x": 4}, {"y": 5, "x": 4}, {"y": 5, "x": 5}, {"y": 5, "x": 6}, {"y": 5, "x": 7}, {"y": 5, "x": 8}, {"y": 4, "x": 8}, {"y": 4, "x": 7}, {"y": 4, "x": 6}, {"y": 4, "x": 5}, {"y": 4, "x": 4}, {"y": 3, "x": 4}, {"y": 3, "x": 3}, {"y": 2, "x": 3}, {"y": 1, "x": 3}, {"y": 0, "x": 3}, {"y": 0, "x": 2}]}], "food": [{"y": 2, "x": 5}, {"y": 3, "x": 9}, {"y": 1, "x": 7}], "width": 11}, "game": {"id": "816e4e61-65d2-4815-95af-9a063238724b"}, "turn": 148}
game = Game(move)
game.update_game(move)

print game.kill_moves
print game.get_move()
print game.shout
