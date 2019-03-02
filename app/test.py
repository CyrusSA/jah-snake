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
#wtf = {"board": {"food": [{"x": 2, "y": 10}, {"x": 12, "y": 0}, {"x": 5, "y": 18}, {"x": 2, "y": 9}], "height": 19, "snakes": [{"body": [{"x": 4, "y": 2}, {"x": 3, "y": 2}, {"x": 2, "y": 2}], "name": "MikeShi42 / Boba Addict", "id": "gs_Rgp3B9Pky6MPJMTBSFS69wCS", "health": 96}, {"body": [{"x": 17, "y": 13}, {"x": 17, "y": 14}, {"x": 17, "y": 15}, {"x": 17, "y": 16}, {"x": 17, "y": 17}], "name": "12kelly12 / BJK's Snake", "id": "gs_QmGpPhCKc4BHRgdc68XQdCBW", "health": 98}, {"body": [{"x": 3, "y": 15}, {"x": 2, "y": 15}, {"x": 2, "y": 16}], "name": "Xe / Pyra", "id": "gs_bpCpKJryGRrgdx8gCgDTmr4f", "health": 96}, {"body": [{"x": 9, "y": 5}, {"x": 9, "y": 4}, {"x": 9, "y": 3}], "name": "LeoRager / V3 Snake", "id": "gs_cHDk8Jgkq9bmHBXFVC6wVFKF", "health": 96}, {"body": [{"x": 18, "y": 6}, {"x": 17, "y": 6}, {"x": 17, "y": 7}], "name": "CyrusSA / Jah-Snake", "id": "gs_k89S6VkCFkG6qkVPwjPDqVC8", "health": 96}], "width": 19}, "game": {"id": "3e95cb54-c5d4-440c-9945-3e9309a37eca"}, "turn": 4, "you": {"body": [{"x": 18, "y": 6}, {"x": 17, "y": 6}, {"x": 17, "y": 7}], "name": "CyrusSA / Jah-Snake", "id": "gs_k89S6VkCFkG6qkVPwjPDqVC8", "health": 96}}

# game = Game(start)

# game.update_game(move1)
# print game.get_move()
# game.update_game(move2)
# print game.get_move()
# game.update_game(move3)
# print game.get_move()
# game.update_game(wtf)
# print game.board.has_node((18, 6))
# print game.board.has_node((17, 7))