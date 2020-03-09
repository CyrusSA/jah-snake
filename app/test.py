from game import Game
import networkx as nx

request = {
  "game": {
    "id": "game-id-string"
  },
  "turn": 4,
  "board": {
    "height": 5,
    "width": 5,
    "food": [
      {
        "x": 1,
        "y": 3
      }
    ],
    "snakes": [
      {
        "id": "snake-id-string",
        "name": "Sneky Snek",
        "health": 90,
        "body": [
            {
                "x": 0,
                "y": 2
            },
            {
                "x": 0,
                "y": 3
            },
            {
                "x": 0,
                "y": 4
            }
        ]
      }
    ]
  },
  "you": {
    "id": "snake-id-string",
    "name": "Sneky Snek",
    "health": 90,
    "body": [
      {
        "x": 0,
        "y": 2
      },
        {
            "x": 0,
            "y": 3
        },
      {
        "x": 0,
        "y": 4
      }
    ]
  }
}

start = {"turn": 0, "you": {"name": "CyrusSA / test1", "body": [{"x": 1, "y": 1}, {"x": 1, "y": 1}, {"x": 1, "y": 1}], "id": "gs_gB8P3T4wCC8QR3gtRTcbkd89", "health": 100}, "board": {"snakes": [{"name": "CyrusSA / test1", "body": [{"x": 1, "y": 1}, {"x": 1, "y": 1}, {"x": 1, "y": 1}], "id": "gs_gB8P3T4wCC8QR3gtRTcbkd89", "health": 100}], "food": [{"x": 2, "y": 3}], "width": 11, "height": 11}, "game": {"id": "ca1e31ef-39fe-4978-b92a-a1d46ca70449"}}
move1 = {"turn": 0, "you": {"name": "CyrusSA / test1", "body": [{"x": 1, "y": 1}, {"x": 1, "y": 1}, {"x": 1, "y": 1}], "id": "gs_gB8P3T4wCC8QR3gtRTcbkd89", "health": 100}, "board": {"snakes": [{"name": "CyrusSA / test1", "body": [{"x": 1, "y": 1}, {"x": 1, "y": 1}, {"x": 1, "y": 1}], "id": "gs_gB8P3T4wCC8QR3gtRTcbkd89", "health": 100}], "food": [{"x": 2, "y": 3}], "width": 11, "height": 11}, "game": {"id": "ca1e31ef-39fe-4978-b92a-a1d46ca70449"}}
move2 = {"turn": 1, "you": {"name": "CyrusSA / test1", "body": [{"x": 1, "y": 0}, {"x": 1, "y": 1}, {"x": 1, "y": 1}], "id": "gs_gB8P3T4wCC8QR3gtRTcbkd89", "health": 99}, "board": {"snakes": [{"name": "CyrusSA / test1", "body": [{"x": 1, "y": 0}, {"x": 1, "y": 1}, {"x": 1, "y": 1}], "id": "gs_gB8P3T4wCC8QR3gtRTcbkd89", "health": 99}], "food": [{"x": 2, "y": 3}], "width": 11, "height": 11}, "game": {"id": "ca1e31ef-39fe-4978-b92a-a1d46ca70449"}}
move3 = {"game": {"id": "a369c052-c1af-4f26-92e8-e8158ca82290"}, "turn": 2, "board": {"width": 11, "food": [{"x": 6, "y": 9}], "height": 11, "snakes": [{"body": [{"x": 2, "y": 0}, {"x": 1, "y": 0}, {"x": 1, "y": 1}], "name": "CyrusSA / test1", "id": "gs_BCccP3kPjGFcxMxGdRvYFKPF", "health": 49}]}, "you": {"body": [{"x": 2, "y": 0}, {"x": 1, "y": 0}, {"x": 1, "y": 1}], "name": "CyrusSA / test1", "id": "gs_BCccP3kPjGFcxMxGdRvYFKPF", "health": 49}}

# 120 -> 121 snake turns into head of other snake
move120 =  {"you": {"body": [{"y": 8, "x": 2}, {"y": 9, "x": 2}, {"y": 10, "x": 2}, {"y": 10, "x": 3}, {"y": 9, "x": 3}, {"y": 8, "x": 3}, {"y": 8, "x": 4}, {"y": 8, "x": 4}], "name": "Jah-Snake", "health": 100, "id": "gs_fXrdTjPD7wWXxqyWybm7H3fR", "shout": ""}, "turn": 120, "game": {"id": "741e705d-bf8d-473e-b20a-88925b6049b4"}, "board": {"food": [{"y": 1, "x": 10}, {"y": 5, "x": 9}, {"y": 9, "x": 8}, {"y": 4, "x": 9}, {"y": 10, "x": 9}, {"y": 3, "x": 9}, {"y": 9, "x": 0}, {"y": 7, "x": 6}, {"y": 10, "x": 7}, {"y": 7, "x": 8}, {"y": 3, "x": 8}, {"y": 6, "x": 5}, {"y": 9, "x": 1}], "snakes": [{"body": [{"y": 7, "x": 1}, {"y": 6, "x": 1}, {"y": 6, "x": 2}, {"y": 5, "x": 2}, {"y": 4, "x": 2}, {"y": 3, "x": 2}, {"y": 2, "x": 2}, {"y": 2, "x": 3}, {"y": 1, "x": 3}, {"y": 1, "x": 4}, {"y": 2, "x": 4}, {"y": 3, "x": 4}, {"y": 4, "x": 4}, {"y": 4, "x": 3}, {"y": 4, "x": 3}], "name": "dumb-snakev04", "health": 100, "id": "gs_9grhT4xgp63RgQtVMqYvc3SV", "shout": ""}, {"body": [{"y": 8, "x": 2}, {"y": 9, "x": 2}, {"y": 10, "x": 2}, {"y": 10, "x": 3}, {"y": 9, "x": 3}, {"y": 8, "x": 3}, {"y": 8, "x": 4}, {"y": 8, "x": 4}], "name": "Jah-Snake", "health": 100, "id": "gs_fXrdTjPD7wWXxqyWybm7H3fR", "shout": ""}], "width": 11, "height": 11}}
move121 = {"you": {"body": [{"y": 7, "x": 2}, {"y": 8, "x": 2}, {"y": 9, "x": 2}, {"y": 10, "x": 2}, {"y": 10, "x": 3}, {"y": 9, "x": 3}, {"y": 8, "x": 3}, {"y": 8, "x": 4}], "name": "Jah-Snake", "health": 99, "id": "gs_fXrdTjPD7wWXxqyWybm7H3fR", "shout": ""}, "turn": 121, "game": {"id": "741e705d-bf8d-473e-b20a-88925b6049b4"}, "board": {"food": [{"y": 1, "x": 10}, {"y": 5, "x": 9}, {"y": 9, "x": 8}, {"y": 4, "x": 9}, {"y": 10, "x": 9}, {"y": 3, "x": 9}, {"y": 9, "x": 0}, {"y": 7, "x": 6}, {"y": 10, "x": 7}, {"y": 7, "x": 8}, {"y": 3, "x": 8}, {"y": 6, "x": 5}, {"y": 9, "x": 1}], "snakes": [{"body": [{"y": 7, "x": 2}, {"y": 7, "x": 1}, {"y": 6, "x": 1}, {"y": 6, "x": 2}, {"y": 5, "x": 2}, {"y": 4, "x": 2}, {"y": 3, "x": 2}, {"y": 2, "x": 2}, {"y": 2, "x": 3}, {"y": 1, "x": 3}, {"y": 1, "x": 4}, {"y": 2, "x": 4}, {"y": 3, "x": 4}, {"y": 4, "x": 4}, {"y": 4, "x": 3}], "name": "dumb-snakev04", "health": 99, "id": "gs_9grhT4xgp63RgQtVMqYvc3SV", "shout": ""}], "width": 11, "height": 11}}

movelol = {"game": {"id": "a7af2611-20e3-4562-8a76-d32961b659e5"}, "you": {"name": "Jah-Snake", "shout": "", "health": 69, "id": "gs_FbtChFgPGbPwMTm43HwfVpB4", "body": [{"y": 9, "x": 6}, {"y": 9, "x": 7}, {"y": 9, "x": 8}]}, "turn": 31, "board": {"height": 11, "snakes": [{"name": "DumbButGood", "shout": "", "health": 94, "id": "gs_gf64G9vQ8QJWWpYK3JR8mhgC", "body": [{"y": 10, "x": 1}, {"y": 10, "x": 0}, {"y": 9, "x": 0}, {"y": 8, "x": 0}, {"y": 7, "x": 0}]}, {"name": "dumb-snakev04", "shout": "", "health": 94, "id": "gs_dtPMB7mqgp7rfh94Mh8cMvRX", "body": [{"y": 7, "x": 6}, {"y": 6, "x": 6}, {"y": 6, "x": 7}, {"y": 6, "x": 8}, {"y": 5, "x": 8}, {"y": 4, "x": 8}, {"y": 3, "x": 8}, {"y": 3, "x": 7}]}, {"name": "Jah-Snake", "shout": "", "health": 69, "id": "gs_FbtChFgPGbPwMTm43HwfVpB4", "body": [{"y": 9, "x": 6}, {"y": 9, "x": 7}, {"y": 9, "x": 8}]}], "width": 11, "food": [{"y": 10, "x": 3}, {"y": 9, "x": 1}, {"y": 10, "x": 5}]}}
move00 = {"game": {"id": "a7af2611-20e3-4562-8a76-d32961b659e5"}, "you": {"name": "Jah-Snake", "shout": "", "health": 68, "id": "gs_FbtChFgPGbPwMTm43HwfVpB4", "body": [{"y": 9, "x": 5}, {"y": 9, "x": 6}, {"y": 9, "x": 7}]}, "turn": 32, "board": {"height": 11, "snakes": [{"name": "DumbButGood", "shout": "", "health": 100, "id": "gs_gf64G9vQ8QJWWpYK3JR8mhgC", "body": [{"y": 9, "x": 1}, {"y": 10, "x": 1}, {"y": 10, "x": 0}, {"y": 9, "x": 0}, {"y": 8, "x": 0}, {"y": 8, "x": 0}]}, {"name": "dumb-snakev04", "shout": "", "health": 93, "id": "gs_dtPMB7mqgp7rfh94Mh8cMvRX", "body": [{"y": 8, "x": 6}, {"y": 7, "x": 6}, {"y": 6, "x": 6}, {"y": 6, "x": 7}, {"y": 6, "x": 8}, {"y": 5, "x": 8}, {"y": 4, "x": 8}, {"y": 3, "x": 8}]}, {"name": "Jah-Snake", "shout": "", "health": 68, "id": "gs_FbtChFgPGbPwMTm43HwfVpB4", "body": [{"y": 9, "x": 5}, {"y": 9, "x": 6}, {"y": 9, "x": 7}]}], "width": 11, "food": [{"y": 10, "x": 3}, {"y": 10, "x": 5}]}}
move11 = {"game": {"id": "a7af2611-20e3-4562-8a76-d32961b659e5"}, "you": {"name": "Jah-Snake", "shout": "", "health": 100, "id": "gs_FbtChFgPGbPwMTm43HwfVpB4", "body": [{"y": 10, "x": 5}, {"y": 9, "x": 5}, {"y": 9, "x": 6}, {"y": 9, "x": 6}]}, "turn": 33, "board": {"height": 11, "snakes": [{"name": "DumbButGood", "shout": "", "health": 99, "id": "gs_gf64G9vQ8QJWWpYK3JR8mhgC", "body": [{"y": 8, "x": 1}, {"y": 9, "x": 1}, {"y": 10, "x": 1}, {"y": 10, "x": 0}, {"y": 9, "x": 0}, {"y": 8, "x": 0}]}, {"name": "dumb-snakev04", "shout": "", "health": 92, "id": "gs_dtPMB7mqgp7rfh94Mh8cMvRX", "body": [{"y": 8, "x": 5}, {"y": 8, "x": 6}, {"y": 7, "x": 6}, {"y": 6, "x": 6}, {"y": 6, "x": 7}, {"y": 6, "x": 8}, {"y": 5, "x": 8}, {"y": 4, "x": 8}]}, {"name": "Jah-Snake", "shout": "", "health": 100, "id": "gs_FbtChFgPGbPwMTm43HwfVpB4", "body": [{"y": 10, "x": 5}, {"y": 9, "x": 5}, {"y": 9, "x": 6}, {"y": 9, "x": 6}]}], "width": 11, "food": [{"y": 10, "x": 3}]}}
move22 = {"game": {"id": "a7af2611-20e3-4562-8a76-d32961b659e5"}, "you": {"name": "Jah-Snake", "shout": "", "health": 99, "id": "gs_FbtChFgPGbPwMTm43HwfVpB4", "body": [{"y": 10, "x": 6}, {"y": 10, "x": 5}, {"y": 9, "x": 5}, {"y": 9, "x": 6}]}, "turn": 34, "board": {"height": 11, "snakes": [{"name": "DumbButGood", "shout": "", "health": 98, "id": "gs_gf64G9vQ8QJWWpYK3JR8mhgC", "body": [{"y": 7, "x": 1}, {"y": 8, "x": 1}, {"y": 9, "x": 1}, {"y": 10, "x": 1}, {"y": 10, "x": 0}, {"y": 9, "x": 0}]}, {"name": "dumb-snakev04", "shout": "", "health": 91, "id": "gs_dtPMB7mqgp7rfh94Mh8cMvRX", "body": [{"y": 8, "x": 4}, {"y": 8, "x": 5}, {"y": 8, "x": 6}, {"y": 7, "x": 6}, {"y": 6, "x": 6}, {"y": 6, "x": 7}, {"y": 6, "x": 8}, {"y": 5, "x": 8}]}, {"name": "Jah-Snake", "shout": "", "health": 99, "id": "gs_FbtChFgPGbPwMTm43HwfVpB4", "body": [{"y": 10, "x": 6}, {"y": 10, "x": 5}, {"y": 9, "x": 5}, {"y": 9, "x": 6}]}], "width": 11, "food": [{"y": 10, "x": 3}]}}

game = Game(start)
game.update_game(movelol)
print game.just_ate
game.update_game(move00)
print game.just_ate
game.update_game(move11)
print game.just_ate
game.update_game(move22)
print game.just_ate

print game.head, game.tail
for path in nx.all_simple_paths(game.board, game.head, game.tail, 3):
    if len(path) > 3:
        print path


# game.update_game(move1)
# print game.get_move()
# game.update_game(move2)
# print game.get_move()
# game.update_game(move3)
# print game.get_move()
# game.update_game(wtf)
# print game.board.has_node((18, 6))
# print game.board.has_node((17, 7))
