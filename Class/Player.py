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
    def draw(cls, cardsDrawn: List[Card]):
        if len(cardsDrawn) <= 20:
            cls.hand = cls.hand + cardsDrawn
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

