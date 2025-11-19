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

class DrawOptions(Enum):
    ONE = 1
    TWO = 2
    THREE = 3

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
    def create(self):
        red_cards: List[Card] = [Card(CardColor.RED, number) for number in range(1, 10)]
        green_cards: List[Card] = [Card(CardColor.GREEN, number) for number in range(1, 10)]
        blue_cards: List[Card] = [Card(CardColor.BLUE, number) for number in range(1, 10)]
        black_cards: List[Card] = [Card(CardColor.BLACK, number) for number in range(1, 10)]
        yellow_cards: List[Card] = [Card(CardColor.YELLOW, number) for number in range(1, 10)]

        all_cards = red_cards + green_cards + blue_cards + black_cards + yellow_cards
        all_cards = all_cards + all_cards
        return Deck(cards=deque(all_cards))


    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self) -> List[Card]:
        cards_dealt: List[Card] = []
        for i in range(4):
            cards_dealt.append(self.cards.popleft())
        return cards_dealt

    def draw_cards(self, number_of_cards: int) -> List[Card]:
        cards_drawn: List[Card] = []
        for i in range(number_of_cards):
            cards_drawn.append(self.cards.popleft())
        return cards_drawn

    def add_cards(self, cards_to_add: List[Card]):
        self.cards.extend(cards_to_add)

@dataclass
class GameState:
    players: Deque[Player] # 0. Current Player 1. Next/Previous Player 2. Previous Player
    currentPlayer: Player
    chosenPlayer: Player
    deck: Deck = Deck.create()
    state: State = State.CONTINUE


