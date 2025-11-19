import random

from typing import List, Dict

import uuid

from enum import Enum, auto

from dataclasses import dataclass

from Class.Classes import Card, CardColor


@dataclass
class PlayerMove(Enum):
    DRAW_ONE = auto()
    DRAW = auto()
    TAKE = auto()
    PASS = auto()
    DISCARD_CARD = auto()
    DISCARD_VALID_CARDS = auto()
    END_TURN = auto()


@dataclass
class PlayerType(Enum):
    COMPUTER = auto()
    HUMAN = auto()


@dataclass
class Player:
    playerId: uuid.UUID
    hand: List[Card]
    type: PlayerType

    def draw(self, cards_drawn: List[Card]):
        if len(cards_drawn) <= 20:
            self.hand = self.hand + cards_drawn
        else:
           raise ValueError("Player cannot hold more than 20 cards!")

    def shuffle_hand(self):
        random.shuffle(self.hand)

    def take_card(self, card: Card):
        self.hand.append(card)

    def lose_card(self, card: int) -> Card:
        return self.hand.pop(card)

    def discard_card(self, card: Card):
        self.hand.remove(card)

    def discard_valid_cards(self, cards: List[Card]):
        for card in cards:
            self.hand.remove(card) # TODO Confirm if remove(card) only removes one instance of the card if there are two