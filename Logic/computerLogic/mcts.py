# Here goes nothing yo - don't know what I am about to produce
from Logic.Classes import *



class hash_game_state:
    def __init__(self,game_state: GameState):
        self.current_hand = tuple (sorted((card.color, card.number) for card in game_state.current_player.hand))

        self.deck_size = len(game_state.deck.cards)
        self.opponent_sizes = tuple()



    def __hash__(self):
        return hash((self.current_))


class MonteCarlo:
    def __init__(self):
        pass

    def get_optimal_move(self):
        pass