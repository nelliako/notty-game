from typing import List

from Class.Classes import Deck, Player, PlayerMove
from Logic.ValidateCardLogic import contains_valid_group


def player_logic(player: Player, deck: Deck, available_moves: List[PlayerMove]):
    # Does the player have a valid card group?
    cards_in_hand = len(player.hand)
    valid_card_group = contains_valid_group(player.hand)


        