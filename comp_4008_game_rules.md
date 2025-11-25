# Notty Game Rules

# Overview

Your group project will be related to the new game that we called Notty. This document gives the rules of the game.

Description of the GameNotty is a card game played with cards that are numbered and coloured. Each card has a **colour (red, green, yellow, black and blue)** and a number **(1 to 9)**. There are exactly **two cards for each combination of colour and number**, making a **total of 90 cards in the deck**.

The game is designed for **two** or **three** players.

## Setup

At the beginning of the game, the deck is shuffled, and each player is dealt 4 cards (called their hand).

All players’ cards are face up throughout the game, meaning everyone can see each other’s cards.

All the cards in the deck are always face down.

## Gameplay

Players take turns. On a player’s turn, they can perform any of the following actions, in an arbitrary order:

1. (At most once per turn) Draw up to 3 cards from the top of the deck. They do not need to decide on the number of cards to be drawn in advance, however they cannot see the face of the cards drawn until they finish the drawing.
2. (At most once per turn) Choose another player and take a random card from them (in the physical game, the chosen player would shuffle their hand face-down and allow the current player to pick one randomly).
3. (At most once per turn) Draw the top card from the deck, then choose a card from the hand and discard it. (They may discard the card they just drew.)
4. (Any number of times per turn) Discard a valid group of cards. A valid group is either:
    - A sequence of at least three cards of the same colour with consecutive numbers (e.g. blue 4, blue 5 and blue 6)
    - A set of at least four cards of the same number but different colours (e.g. blue 4, green 4 and red 4). Note that no repeated colours are allowed in this type of group (e.g. blue 4, red 4 and blue 4 is not a valid group)

Note that a player is allowed to pass, i.e. take no actions.

For example, the player could take action 2, then 4, then 3, then 1, then 4 again, and then end their turn. A player cannot have more than 20 cards in their hand at any point; actions 1 and 2 can become not available by this rule.

Every time that cards are discarded, they are added to the deck, and then the entire deck is reshuffled.

## Goal of the game
The first player to empty their hand either by:
1. discarding their last cards, or
2. losing their last card via action (2) wins the game immediately.
