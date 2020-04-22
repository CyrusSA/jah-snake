from game import Game

move = {"game": {"id": "64aecf67-255f-4743-b871-29455e443442"}, "you": {"shout": "Strat: tail", "body": [{"y": 4, "x": 5}, {"y": 4, "x": 4}, {"y": 3, "x": 4}, {"y": 2, "x": 4}, {"y": 2, "x": 5}, {"y": 3, "x": 5}], "name": "santino-marella", "health": 87, "id": "gs_WdVKSdYb8qTkymgHJSFtmmcX"}, "turn": 73, "board": {"food": [{"y": 10, "x": 9}], "width": 11, "height": 11, "snakes": [{"shout": "", "body": [{"y": 6, "x": 9}, {"y": 5, "x": 9}, {"y": 4, "x": 9}, {"y": 3, "x": 9}, {"y": 2, "x": 9}, {"y": 2, "x": 10}, {"y": 3, "x": 10}, {"y": 4, "x": 10}, {"y": 5, "x": 10}, {"y": 6, "x": 10}], "name": "David Hasslesnake", "health": 97, "id": "gs_xD3kkhqqrwyQSK4cjBhqMtvM"}, {"shout": "Strat: tail", "body": [{"y": 4, "x": 5}, {"y": 4, "x": 4}, {"y": 3, "x": 4}, {"y": 2, "x": 4}, {"y": 2, "x": 5}, {"y": 3, "x": 5}], "name": "santino-marella", "health": 87, "id": "gs_WdVKSdYb8qTkymgHJSFtmmcX"}, {"shout": "Duration: 9", "body": [{"y": 2, "x": 3}, {"y": 1, "x": 3}, {"y": 1, "x": 4}, {"y": 1, "x": 5}, {"y": 1, "x": 6}, {"y": 1, "x": 7}, {"y": 1, "x": 8}, {"y": 2, "x": 8}, {"y": 3, "x": 8}, {"y": 4, "x": 8}, {"y": 5, "x": 8}, {"y": 6, "x": 8}, {"y": 7, "x": 8}, {"y": 8, "x": 8}], "name": "Sir Pent", "health": 97, "id": "gs_D6FdjJCXdSFPWHCPm8KTCgvJ"}]}}
game = Game(move)
game.update_game(move)

print game.get_move()
print game.shout
