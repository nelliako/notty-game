from typing import List, Dict

from Logic.Classes import Card, CardColor


def colours_identical(cards: List[Card]) -> list[Card] | None:
     # number of cards per color
    colors = {}
    # stores card for each color & number
    colors_cards: Dict[CardColor, Dict[int, Card]] = {}

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

        consecutive_numbers = 0
        for i in range(len(keys)):
            if (keys[i] + 1) in keys:
                consecutive_numbers += 1

        # print(consecutive_numbers)
        if consecutive_numbers >= 2:
            return [colors_cards[color][number] for number in colors_cards[color]]

    return None


def numbers_identical(cards: List[Card]) -> list[Card] | None:
    number_cards: Dict[int, List[Card]] = {}

    for card in set(cards):
        number = card.number

        if number not in number_cards:
            number_cards[number] = []
            number_cards[number].append(card)
        else:
            number_cards[number].append(card)

    for number in number_cards:
        if len(number_cards[number]) < 3:
            continue
        else:
            return number_cards[number]

    return None


def contains_valid_group(cards: List[Card]) -> list[Card] | None:
    number_cards = numbers_identical(cards)
    color_cards = colours_identical(cards)
    if number_cards is not None:
        # print("numbersIdentical")
        return number_cards

    if color_cards is not None:
        # print("coloursIdentical")
        return color_cards

    return None
