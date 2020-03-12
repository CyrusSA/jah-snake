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
move1 = {"turn": 1, "game": {"id": "a8830f9f-c064-4673-a744-273d720eb908"}, "you": {"id": "gs_T6jCJTv3dBbqVKrhfvqhMR8D", "health": 99, "name": "Jah-Snake", "shout": "", "body": [{"x": 5, "y": 8}, {"x": 5, "y": 9}, {"x": 5, "y": 9}]}, "board": {"height": 11, "snakes": [{"id": "gs_T6jCJTv3dBbqVKrhfvqhMR8D", "health": 99, "name": "Jah-Snake", "shout": "", "body": [{"x": 5, "y": 8}, {"x": 5, "y": 9}, {"x": 5, "y": 9}]}], "width": 11, "food": [{"x": 9, "y": 4}]}}
movelol =  {"turn": 2, "game": {"id": "a8830f9f-c064-4673-a744-273d720eb908"}, "you": {"id": "gs_T6jCJTv3dBbqVKrhfvqhMR8D", "health": 98, "name": "Jah-Snake", "shout": "", "body": [{"x": 6, "y": 8}, {"x": 5, "y": 8}, {"x": 5, "y": 9}]}, "board": {"height": 11, "snakes": [{"id": "gs_T6jCJTv3dBbqVKrhfvqhMR8D", "health": 98, "name": "Jah-Snake", "shout": "", "body": [{"x": 6, "y": 8}, {"x": 5, "y": 8}, {"x": 5, "y": 9}]}], "width": 11, "food": [{"x": 9, "y": 4}, {"x": 0, "y": 8}]}}

game = Game(start)
game.update_game(move1)
game.update_game(movelol)

game.get_move()

print game.extend_and_return_snakes([5,6])
print game.snakes



# game.update_game(move1)
# print game.get_move()
# game.update_game(move2)
# print game.get_move()
# game.update_game(move3)
# print game.get_move()
# game.update_game(wtf)
# print game.board.has_node((18, 6))
# print game.board.has_node((17, 7))
