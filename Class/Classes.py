import random
import uuid
from collections import deque
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Deque

import pygame
from pygame import Color


class State(Enum):
    WON = auto()
    CONTINUE = auto()


class DrawOptions(Enum):
    ONE = 1
    TWO = 2
    THREE = 3


class CardColor(Enum):
    RED = Color(220, 20, 60, 255)
    GREEN = Color(0, 168, 107, 255)
    BLUE = Color(0, 71, 171, 255)
    BLACK = Color(0, 0, 0, 255)
    YELLOW = Color(250, 218, 94, 255)


@dataclass
class Card:
    def __init__(self, card_color, number):
        super().__init__()
        # self.image = image
        # self.original_image = image
        self.hover_image = None
        self.clicked_image = None
        # self.rect = self.image.get_rect()
        # self.rect.x = x
        # self.rect.y = y
        self.on_hover = False
        self.is_selected = False
        self.color = card_color
        self.number = number

    # TODO(Darron from Nellia): make this type hashable for colours_identical. 

    def __repr__(self):
        return f"Card({self.color}, {self.number})"

    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.color == other.color and self.number == other.number

    def __hash__(self):
        return hash((self.color, self.number))

    def update(self, events: List[pygame.event.Event]):
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        self.on_hover = self.rect.collidepoint(mouse_pos)

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                if self.rect.collidepoint(event.pos):
                    self.is_selected = not self.is_selected


        self.image = self.hover_image if self.on_hover else self.original_image
        self.image = self.clicked_image if self.is_selected else self.original_image


def create_deck():
    red_cards: List[Card] = [Card(CardColor.RED, number) for number in range(1, 10)]
    green_cards: List[Card] = [Card(CardColor.GREEN, number) for number in range(1, 10)]
    blue_cards: List[Card] = [Card(CardColor.BLUE, number) for number in range(1, 10)]
    black_cards: List[Card] = [Card(CardColor.BLACK, number) for number in range(1, 10)]
    yellow_cards: List[Card] = [Card(CardColor.YELLOW, number) for number in range(1, 10)]

    all_cards = red_cards + green_cards + blue_cards + black_cards + yellow_cards
    all_cards = all_cards + all_cards
    random.shuffle(all_cards)
    return Deque(all_cards)


class Deck:
    def __init__(self):
        self.cards = create_deck()

    def shuffle_deck(self):
        temp_list = list(self.cards)
        random.shuffle(temp_list)
        self.cards = deque(temp_list)

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

class PlayerMove(Enum):
    DRAW_ONE = auto()
    DRAW = auto()
    TAKE = auto()
    PASS = auto()
    DISCARD_CARD = auto()
    DISCARD_VALID_CARDS = auto()
    END_TURN = auto()


class PlayerType(Enum):
    COMPUTER_EASY = auto()
    COMPUTER_MEDIUM = auto()
    COMPUTER_HARD = auto()
    HUMAN = auto()


@dataclass
class Player:
    '''
    Image can be none, in this case no updates are made.
    '''
    def __init__(self, player_id, hand, player_type, name, image = None, x = None, y = None):
        super().__init__()
        self.image = image
        self.original_image = image
        self.hover_image = None
        self.clicked_image = None
        if image is not None:
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
        self.on_hover = False
        self.is_selected = False
        self.player_id: uuid.UUID = player_id
        self.name = name
        self.hand: List[Card] = hand
        self.type: PlayerType = player_type

    def __repr__(self):
        return f"{self.player_id}"

    def update(self, events: List[pygame.event.Event]):
        if self.image is None:
            return
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        self.on_hover = self.rect.collidepoint(mouse_pos)

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                if self.rect.collidepoint(event.pos):
                    self.is_selected = not self.is_selected

        self.image = self.hover_image if self.on_hover else self.original_image
        self.image = self.clicked_image if self.is_selected else self.original_image

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

    def discard_card(self) -> Card:
        return self.hand.pop()

    def discard_valid_cards(self, cards: List[Card]):
        for card in cards:
            self.hand.remove(
                card)  # TODO Confirm if remove(card) only removes one instance of the card if there are two


class GameState:
    def __init__(self, players: Deque[Player], deck: Deck):
        self.players = players
        self.current_player: Player = None
        self.chosen_player: Player = None
        self.deck = deck
        self.state = State.CONTINUE
        self.number_players = 2
        self.player_difficulty = PlayerType.COMPUTER_EASY

    def set_players(self, number):
        self.number_players = number
        print(f"Number of players selected: {self.number_players}!")

    def set_player_difficulty(self, difficulty):
        self.player_difficulty = difficulty
        print(f"Player_difficulty selected: {self.player_difficulty}!")


