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

    @classmethod
    def draw(cls, cards_drawn: List[Card]):
        if len(cards_drawn) <= 20:
            cls.hand = cls.hand + cards_drawn
        else:
           raise ValueError("Player cannot hold more than 20 cards!")

    @classmethod
    def shuffle_hand(cls):
        random.shuffle(cls.hand)

    @classmethod
    def take_card(cls, card: Card):
        cls.hand.append(card)

    @classmethod
    def lose_card(cls, card: int) -> Card:
        return cls.hand.pop(card)

    @classmethod
    def discard_card(cls, card: Card):
        cls.hand.remove(card)

    @classmethod
    def discard_valid_cards(cls, cards: List[Card]):
        for card in cards:
            cls.hand.remove(card) # TODO Confirm if remove(card) only removes one instance of the card if there are two