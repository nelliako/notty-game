import random

from pygame import Color
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Deque
from collections import deque

from Class.Player import Player


@dataclass
class State(Enum):
    WON = auto()
    CONTINUE = auto()

@dataclass
class CardColor(Enum):
    RED = Color(220, 20, 60, 255)
    GREEN = Color(0, 168, 107, 255)
    BLUE = Color(0, 71, 171, 255)
    BLACK = Color(0, 0, 0, 255)
    YELLOW = Color(250, 218, 94, 255)

@dataclass
class Card:
    color: CardColor
    number: int

@dataclass
class Deck:
    cards: Deque[Card]

    @classmethod
    def create(cls):
        redCards: List[Card] = [Card(CardColor.RED, number) for number in range(1, 10)]
        greenCards: List[Card] = [Card(CardColor.GREEN, number) for number in range(1, 10)]
        blueCards: List[Card] = [Card(CardColor.BLUE, number) for number in range(1, 10)]
        blackCards: List[Card] = [Card(CardColor.BLACK, number) for number in range(1, 10)]
        yellowCards: List[Card] = [Card(CardColor.YELLOW, number) for number in range(1, 10)]

        allCards = redCards + greenCards + blueCards + blackCards + yellowCards
        allCards = allCards + allCards
        return Deck(cards=deque(allCards))

    @classmethod
    def shuffle(cls):
        random.shuffle(cls.cards)

    @classmethod
    def deal(cls) -> List[Card]:
        cardsDealt: List[Card] = []
        for i in range(4):
            cardsDealt.append(cls.cards.popleft())
        return cardsDealt

    @classmethod
    def draw_cards(cls, numberOfCards: int) -> List[Card]:
        cardsDrawn: List[Card] = []
        for i in range(numberOfCards):
            cardsDrawn.append(cls.cards.popleft())
        return cardsDrawn

    @classmethod
    def add_cards(cls, cardsToAdd: List[Card]):
        cls.cards.extend(cardsToAdd)

@dataclass
class GameState:
    playerQueue: Deque[Player] # 0. Current Player 1. Next/Previous Player 2. Previous Player
    currentPlayer: Player
    chosenPlayer: Player
    deck: Deck = Deck.create()
    state: State = State.CONTINUE


