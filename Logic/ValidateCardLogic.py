import random
from itertools import chain
from typing import List, Dict
from pygame import key
from Logic.Classes import Card, CardColor


def colours_identical(cards: List[Card]) -> list[Card] | None:
    # stores card for each color & number
    colors_cards: Dict[CardColor, Dict[int, Card]] = {}

    
    for card in set(cards):
        color = card.color
        number = card.number

        if color not in colors_cards:
            colors_cards[color] = {}
        
        colors_cards[color][number] = card

    # Check each color for valid sequences
    for color in colors_cards:
        if len(colors_cards[color]) < 3:
            continue
        
        keys = sorted(list(colors_cards[color].keys()))
        for i in range(len(keys) - 2):
            # Check if we have exactly 3 consecutive numbers
            if keys[i+1]== keys[i] + 1 and keys[i+2]== keys[i] + 2:
                return [colors_cards[color][keys[i]],colors_cards[color][keys[i+1]],colors_cards[color][keys[i+2]]]
    return None


def numbers_identical(cards: List[Card]) -> list[Card] | None:
    number_cards: Dict[int, List[Card]] = {}
    for card in set(cards):
        number= card.number
        if number not in number_cards:
            number_cards[number] = []
        number_cards[number].append(card)

    for number in number_cards:
        if len(number_cards[number])== 4:
            colors_in_set = set(card.color for card in number_cards[number])
            if len(colors_in_set)== 4:
                return number_cards[number]
    
    return None


def contains_valid_group(cards: List[Card]) -> list[Card] | None:
    number_cards= numbers_identical(cards)
    color_cards= colours_identical(cards)
    

    if number_cards is not None:
        return number_cards
    
    if color_cards is not None:
        return color_cards
    return None