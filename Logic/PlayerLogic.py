from typing import List, Dict

from Class.Classes import Card, CardColor
from Class.Player import Player


def valid_card_group(player: Player):
    cards = player.hand


def coloursIdentical(cards: List[Card]) -> list[Card] | None:
    colors = {}
    colorsCards: Dict[CardColor, Dict[int, Card]] = {}

    for card in set(cards):
        color = card.color
        number = card.number

        if color not in colorsCards:
            colors[color] = []
            colorsCards[color] = {}
        else:
            colors[color] = colors[color] + 1

        if not colorsCards[color].get(number, False):
            colorsCards[color][number] = card
        else:
            colorsCards[color][number] = card

    for color in colorsCards:
        if colors[color] < 3:
            continue
        # print(colorsCards)
        keys = sorted(list(colorsCards[color].keys()))
        # print(keys)

        consecutiveNumbers = 0
        for i in range(len(keys)):
            if (keys[i] + 1) in keys:
                consecutiveNumbers += 1

        # print(consecutiveNumbers)
        if consecutiveNumbers >= 2:
            return [colorsCards[color][number] for number in colorsCards[color]]

    return None


def numbersIdentical(cards: List[Card]) -> list[Card] | None:
    numberCards: Dict[int, List[Card]] = {}

    for card in set(cards):
        number = card.number

        if number not in numberCards:
            numberCards[number] = []
            numberCards[number].append(card)
        else:
            numberCards[number].append(card)

    for number in numberCards:
        if len(numberCards[number]) < 3:
            continue
        else:
            return numberCards[number]

    return None


def contains_valid_group(cards: List[Card]) -> list[Card] | None:
    numberCards = numbersIdentical(cards)
    colorCards = coloursIdentical(cards)
    if numberCards is not None:
        # print("numbersIdentical")
        return numberCards

    if colorCards is not None:
        # print("coloursIdentical")
        return colorCards

    return None
