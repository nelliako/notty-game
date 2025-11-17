import uuid
from typing import Deque, List

from Class.Classes import Deck, GameState, State, DrawOptions
from Class.Player import Player, PlayerMove, PlayerType


def determine_player_draw_options(max_card_draw_size: int) -> List[DrawOptions]:
    if max_card_draw_size >= 3:
        return [DrawOptions.ONE, DrawOptions.TWO, DrawOptions.THREE]
    elif max_card_draw_size == 2:
        return [DrawOptions.ONE, DrawOptions.TWO]
    elif max_card_draw_size == 1:
        return [DrawOptions.ONE]
    else:
        return []


def game_loop():
    number_of_players = 3 # int(input("How many players? "))

    # initialize game state & shuffle the deck
    game_state = GameState()
    game_state.deck.shuffle()

    for i in range(number_of_players):
        game_state.players.append(Player(playerId=uuid.uuid4(), type=PlayerType.COMPUTER))

    # deal 4 cards to each player
    for player in game_state.players:
        player.draw(game_state.deck.deal())

    # set the current player to the first player and remove current player from the players list
    game_state.currentPlayer = game_state.players.popleft()

    while game_state.state == State.CONTINUE:
        if any([len(player.hand) == 0 for player in game_state.players]):
            game_state.state = State.WON
            # TODO Say which player won
            break

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
        move: PlayerMove = input("Select a move: ")  # TODO user input

        while move != PlayerMove.END_TURN or move != PlayerMove.PASS or len(moves) != 0:

            if move == PlayerMove.DRAW:
                max_card_draw_size = 20 - len(game_state.currentPlayer.hand)
                # TODO create a variable and maybe replace with a function
                # draw move options
                draw_options = determine_player_draw_options(max_card_draw_size)

                game_state.currentPlayer.draw(game_state.deck.draw_cards(number_of_cards=input(draw_options)))

            if move == PlayerMove.DRAW or move == PlayerMove.TAKE or move == PlayerMove.DRAW_ONE:
                moves.remove(move)

            move = input("Select a move: ")

        # add current player to the end of the `players` list
        game_state.players.append(game_state.currentPlayer)