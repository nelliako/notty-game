import uuid
from collections import deque
from itertools import zip_longest
from typing import Deque, List

import pygame

from Class.Classes import Deck, GameState, State, DrawOptions, Player, PlayerMove, PlayerType, Card
from Logic.ValidateCardLogic import contains_valid_group
from optimal_player_move.player_easy import get_random_move


def determine_player_draw_options(max_card_draw_size: int) -> List[DrawOptions]:
    if max_card_draw_size >= 3:
        return [DrawOptions.ONE, DrawOptions.TWO, DrawOptions.THREE]
    elif max_card_draw_size == 2:
        return [DrawOptions.ONE, DrawOptions.TWO]
    elif max_card_draw_size == 1:
        return [DrawOptions.ONE]
    else:
        return []


def select_card(card: Card, is_selected: bool, selected_card: List[Card]):
    if is_selected & len(selected_card) == 1:
        selected_card[0] = card
    elif is_selected & len(selected_card) == 0:
        selected_card.append(card)


def select_cards(card: Card, is_selected: bool, selected_cards: List[Card]):
    if is_selected:
        selected_cards.append(card)
    else:
        selected_cards.remove(card)


def game_loop():
    number_of_players = 3  # int(input("How many players? "))

    # initialize game state & shuffle the deck
    game_state = GameState(players=deque(), deck=Deck())
    game_state.deck.shuffle_deck()

    for i in range(number_of_players):
        game_state.players.append(Player(player_id=uuid.uuid4(), hand=[], player_type=PlayerType.COMPUTER_EASY))

    # deal 4 cards to each player
    for player in game_state.players:
        player.draw(game_state.deck.draw_cards(4))

    # TODO implement functions for each player type to select moves
    player_moves_map = {
        PlayerType.COMPUTER_EASY: get_random_move, # TODO placeholder function
        PlayerType.COMPUTER_MEDIUM: get_random_move, # TODO placeholder function
        PlayerType.COMPUTER_HARD: get_random_move, # TODO placeholder function
        PlayerType.HUMAN: get_random_move, # TODO placeholder function
    }

    while game_state.state == State.CONTINUE:
        events = pygame.event.get()
        # check if any player has no cards in their hand
        if any([len(player.hand) == 0 for player in game_state.players]):
            game_state.state = State.WON
            # TODO Say which player won
            break

        # set the current player to the first player and remove current player from the players list
        game_state.currentPlayer = game_state.players.popleft()

        available_moves: List[PlayerMove] = [
            PlayerMove.DRAW,
            PlayerMove.TAKE,
            PlayerMove.DRAW_ONE,
            PlayerMove.DISCARD_CARD,
            PlayerMove.DISCARD_VALID_CARDS,
            PlayerMove.PASS,
            PlayerMove.END_TURN
        ]

        restricted_moves: List[PlayerMove] = [
            PlayerMove.DRAW_ONE,
            PlayerMove.DISCARD_CARD,
            PlayerMove.DISCARD_VALID_CARDS,
            PlayerMove.PASS,
            PlayerMove.END_TURN
        ]

        moves: List[PlayerMove] = available_moves if len(game_state.currentPlayer.hand) < 20 else restricted_moves

        make_move = player_moves_map[game_state.currentPlayer.type]
        move, number_of_cards = make_move(player=game_state.currentPlayer, moves=moves)

        while move != PlayerMove.END_TURN or move != PlayerMove.PASS or len(moves) != 0:

            if move == PlayerMove.DRAW:
                max_card_draw_size = 20 - len(game_state.currentPlayer.hand)
                # draw move options
                draw_options = determine_player_draw_options(max_card_draw_size)
                if game_state.currentPlayer.type == PlayerType.HUMAN:
                    number_of_cards = int(input(draw_options))

                game_state.currentPlayer.draw(game_state.deck.draw_cards(number_of_cards=number_of_cards))

            if move == PlayerMove.TAKE:
                selected_card = []

                while not selected_card:
                    for player in game_state.players:
                        player.update(events)
                        if player.is_selected:
                            game_state.chosenPlayer = player
                            game_state.chosenPlayer.shuffle_hand()

                    for card in game_state.chosenPlayer.hand:
                        card.update(events)
                        if card.is_selected:
                            selected_card.append(card)
                        elif card.is_selected == False & (card in selected_card):
                            selected_card.remove(card)

                game_state.chosenPlayer.lose_card(selected_card[0])
                game_state.current_player.take_card(selected_card[0])

            if move == PlayerMove.DRAW_ONE:
                game_state.currentPlayer.draw(game_state.deck.draw_cards(1))

            if move == PlayerMove.DISCARD_CARD:
                discarded_card = game_state.current_player.discard_card()
                game_state.deck.add_cards([discarded_card])
                game_state.deck.shuffle_deck()

            if move == PlayerMove.DISCARD_VALID_CARDS:
                selected_cards = []
                while contains_valid_group(selected_cards) is None:
                    for card in game_state.currentPlayer.hand:
                        card.update(events)

                    selected_cards = [card for card in game_state.currentPlayer.hand if card.is_selected]
                    if contains_valid_group(selected_cards) is None:
                        print("Selected cards must be a valid group.")

                game_state.current_player.discard_valid_cards(selected_cards)
                game_state.deck.add_cards(selected_cards)
                game_state.deck.shuffle_deck()

            if move == PlayerMove.DRAW or move == PlayerMove.TAKE or move == PlayerMove.DRAW_ONE:
                moves.remove(move)

            move = input("Select a move: ")

        # add current player to the end of the `players` list
        game_state.players.append(game_state.currentPlayer)
