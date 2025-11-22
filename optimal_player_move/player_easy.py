from typing import Any, List

import pygame
import numpy as np
import random

from Class.Classes import Player, PlayerMove
from Logic.ValidateCardLogic import contains_valid_group


class player_easy(Player):
    def __init__(self, current_player, valid_moves, image, x, y, player_id, hand, player_type):
        super().__init__(image, x, y, player_id, hand, player_type)
        self.current_player = current_player
        self.available_moves = valid_moves

    # updates the list of available moves for the current player
    def updateAvailableMoves(self):
        # removes moves 1,2,3 only as they are only allowed once
        if self.temp != PlayerMove.DISCARD_VALID_CARDS or self.temp != PlayerMove.PASS or self.temp != PlayerMove.END_TURN:
            self.available_moves.remove(self.temp)
        return self.available_moves

# retrieves and returns a random move from allowed valid moves for the player and also a parameter defining number of cards
def get_random_move(player: Player, moves: List[PlayerMove]) -> tuple[PlayerMove, int]:
    temp: PlayerMove = random.choice(moves)
    parameter = random.choice([1, 2, 3])
    if contains_valid_group(player.hand) is not None:
        return PlayerMove.DISCARD_VALID_CARDS, 0
    if temp == PlayerMove.DRAW:
        return temp, parameter
    return temp, 0

# List of Player Moves for reference
# PlayerMove.DRAW,
# PlayerMove.TAKE,
# PlayerMove.DRAW_ONE,
# PlayerMove.DISCARD_CARD,
# PlayerMove.DISCARD_VALID_CARDS,
# PlayerMove.PASS,
# PlayerMove.END_TURN
