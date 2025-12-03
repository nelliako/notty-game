import random
from itertools import chain
from typing import List, Dict

from pygame import key

from Logic.Classes import Card, CardColor

#TODO: FIX NEEDED
# 1. 4 cards should be returned instead of 3 for same number/different colour
# 2. For example, if blue 1, blue 2, blue 8, blue 9 are present in the hand, they will be returned - bug with colours_identical function in consecutive numbers
# 3. Blue 1, blue 2, blue 3, blue 4, blue 8 are discarded all together - bug here  "return [colors_cards[color][number] for number in colors_cards[color]]""


def colours_identical(cards: List[Card]) -> list[Card] | None:
     # number of cards per color
    colors = {}
    # stores card for each color & number
    colors_cards: Dict[CardColor, Dict[int, Card]] = {}
    cards_to_discard = []

    for card in set(cards):
        color = card.color
        number = card.number

        if color not in colors_cards:
            colors[color] = 1
            colors_cards[color] = {}
        else:
            colors[color] = colors[color] + 1

        if not colors_cards[color].get(number, False):
            colors_cards[color][number] = card
        else:
            colors_cards[color][number] = card

    for color in colors_cards:
        if colors[color] < 3:
            continue
        # print(colors_cards)
        keys = sorted(list(colors_cards[color].keys()))
        # print(keys)

        # create subsets
        subsets = []
        for i in range(len(keys)):
            if i+3 > len(keys):
                break

            for l in range(i+3, len(keys)+1):
                subsets.append(keys[i:l])

        # loop over subsets
        for sub in subsets:
            consecutive_numbers = 0
            # print(f"Subset: {sub}")
            for j in range(1, len(sub)):
                # print(f"Difference: {sub[j]- sub[j-1]}")
                if (sub[j]- sub[j-1]) == 1:
                    consecutive_numbers += 1
                else:
                    break

            # print(f"Number of Consecutive Numbers: {consecutive_numbers}")
            if consecutive_numbers == len(sub)-1:
                cards_sublist = []
                for number in sub:
                    cards_sublist.append(colors_cards[color][number])
                # print(f"adding subset: {cards_sublist}")
                cards_to_discard.append(cards_sublist)

    if len(cards_to_discard) > 0:
        sorted_cards = sorted(cards_to_discard, key=len, reverse=True)
        # for card in sorted_cards:
            # print(f"Discard Cards: {card}")
        return sorted_cards[0]

    return None


def numbers_identical(cards: List[Card]) -> list[Card] | None:
    number_cards: Dict[int, List[Card]] = {}
    validate_cards = []
    for card in set(cards):
        number = card.number

        if number not in number_cards:
            number_cards[number] = []
            number_cards[number].append(card)
        else:
            number_cards[number].append(card)

    for number in number_cards:
        if len(number_cards[number]) < 4:
            continue
        else:
            validate_cards.append(number_cards[number])

    if len(validate_cards) > 0:
        validate_cards = sorted(validate_cards, key=len, reverse=True)
        # for card in validate_cards:
            # print(f"Discard Cards: {card}")
        return validate_cards[0]

    return None


def contains_valid_group(cards: List[Card]) -> list[Card] | None:
    number_cards = numbers_identical(cards)
    color_cards = colours_identical(cards)
    if number_cards is not None and color_cards is not None:
        if len(number_cards) > len(color_cards):
            return number_cards
        elif len(number_cards) < len(color_cards):
            return color_cards
        else:
            return random.choice([number_cards, color_cards])
    if number_cards is not None:
        # print("numbersIdentical")
        return number_cards

    if color_cards is not None:
        # print("coloursIdentical")
        return color_cards

    return None

# def consecutive_numbers(cards: List[Card]) -> list[Card] | None:
