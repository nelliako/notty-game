import random
import uuid
from collections import deque
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Deque

import pygame


class State(Enum):
    WON = auto()
    LOST = auto()
    CONTINUE = auto()


class DrawOptions(Enum):
    ONE = 1
    TWO = 2
    THREE = 3


class CardColor(Enum):
    BLACK = ('black', 1)
    BLUE = ('blue', 2)
    GREEN = ('green', 3)
    RED = ('red', 4)
    YELLOW = ('yellow', 5)

    def __init__(self, display_name, ordinal):
        self.display_name = display_name
        self.ordinal = ordinal


@dataclass
class Card:
    def __init__(self, card_color, number):
        super().__init__()
        self.id = uuid.uuid4()
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
    # Duplicate the deck with NEW Card instances (previously reused same objects)
    all_cards = all_cards + [Card(c.color, c.number) for c in all_cards]
    print(f"Initial Deck Size: {len(all_cards)}")
    random.shuffle(all_cards)
    return deque(all_cards)


class Deck:
    def __init__(self):
        self.cards = create_deck()

    def shuffle_deck(self, trigger_ui=True):
        temp_list = list(self.cards)
        random.shuffle(temp_list)
        self.cards = deque(temp_list)
        # Store reference to game_state if needed for flag
        self._trigger_ui = trigger_ui

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
        self.center_x = x
        self.center_y = y
        self.is_selected = False
        self.player_id: uuid.UUID = player_id
        self.name = name
        self.hand: List[Card] = hand
        self.type: PlayerType = player_type
        self.hide_hand = False

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

    def sort_cards(self):
        self.hand.sort(key=lambda card: (card.color.value, card.number), reverse=True)

class GameState:
    def __init__(self, players: Deque[Player], deck: Deck):
        self.players = players
        self.current_player: Player = None
        self.chosen_player: Player = None
        self.deck = deck
        self.state = State.CONTINUE
        self.number_players = 1
        self.computer_difficulty = PlayerType.COMPUTER_EASY
        self.computer_playing_for_human = False
        self.deck_shuffled = False  # Flag for UI to show shuffle animation


    def set_players(self, number):
        self.number_players = number
        print(f"Number of players selected: {self.number_players}!")

    def set_player_difficulty(self, difficulty):
        self.computer_difficulty = difficulty
        print(f"Player_difficulty selected: {self.computer_difficulty}!")

    def reset_state(self):
        self.current_player = None
        self.chosen_player = None
        self.players = deque()
        self.deck = Deck()
        self.deck_shuffled = False


