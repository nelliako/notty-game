from typing import List

from Class.Classes import Deck
from Class.Player import Player, PlayerMove
from Logic.ValidateCardLogic import contains_valid_group


def player_logic(player: Player, deck: Deck):
    # Does the player have a valid card group?
    cards_in_hand = len(player.hand)
    valid_card_group = contains_valid_group(player.hand)

    available_moves: List[PlayerMove] = [
        PlayerMove.DRAW,
        PlayerMove.TAKE,
        PlayerMove.DRAW_ONE,
        PlayerMove.DISCARD_CARD,
        PlayerMove.DISCARD_VALID_CARDS,
        PlayerMove.PASS,
        PlayerMove.END_TURN
    ] if cards_in_hand < 20 else [
        PlayerMove.DRAW_ONE,
        PlayerMove.DISCARD_CARD,
        PlayerMove.DISCARD_VALID_CARDS,
        PlayerMove.PASS,
        PlayerMove.END_TURN
    ]

        