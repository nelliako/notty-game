from typing import Deque

from Class.Player import Player


def gameLogic(players: Deque[Player]):
    if any([for player in players]):