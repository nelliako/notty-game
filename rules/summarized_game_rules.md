#Notty Game Rules

#Overview

Card Game -> Notty

Each Card = Color + Number

colors = [red, green, yellow, black, blue]

numbers = [1,2,3,4,5,6,7,8,9]

90 Cards -> 2 x Sets of 45 -> 2 x Sets of 5 x Sets of 9

Two Sets of :
> red 1, red 2, red 3, red 4, red 5, red 6, red 7, red 8, red 9
> green 1, green 2, green 3, green 4, green 5, green 6, green 7, green 8, green 9
> yellow 1, yellow 2, yellow 3, yellow 4, yellow 5, yellow 6, yellow 7, yellow 8, yellow 9
> black 1, black 2, black 3, black 4, black 5, black 6, black 7, black 8, black 9
> blue 1, blue 2, blue 3, blue 4, blue 5, blue 6, blue 7, blue 8, blue 9

PLAYERS : 2 , or 3

## Setup

> Starting -> Deck Shuffled

> Each Player Receives -> 4 Random Cards from Shuffled Deck

> All Player Cards -> FACE UP throughout game (everyone can observe)

> Deck -> FACE DOWN always (no player can observe)

## Gameplay

> Turn-based game

> Can make move 1,move 2, move 3, move 4 in any order
> Can make  move 1 once, 
            move 2 once,
            move 3 once
            move 4 any number of times

### MOVE 1:
    > Draw 1 or 2 or 3 Cards from top of Deck.
    > Move finished when cards are faced up.
### MOVE 2:
    > Choose 1 other player, Take 1 Random Card from their hand
    > Other player conceals cards + shuffles -> i.e. Better odds for card player wants, but position unknown
    > So, random choice from other player hand
### MOVE 3:
    > Draw 1 Card from top of Deck > Update Hand
    > Discard any 1 Card from new hand

### MOVE 4:
    > Discard Valid Group in Hand
    ***valid group = set of 3 same color , number consecutives or ,
                     a set of 4 same number different colors

### MOVE 5:
    > Pass turn


> CONSTRAINT : Player may not have more than 20 cards at any point ( move 1,2 invalid if violates )
For example, the player could take action 2, then 4, then 3, then 1, then 4 again, and then end their turn. A player cannot have more than 20 cards in their hand at any point; actions 1 and 2 can become not available by this rule.

> Any discard move -> discarded cards added to DECK -> DECK shuffled

PLAYER GOAL - > EMPTY HAND
                    -> discard last cards
                    -> action(2) takes their last card
##Goal of the game

The first player to empty their hand either by:
1. discarding their last cards, or
2. losing their last card via action (2) wins the game immediately.
