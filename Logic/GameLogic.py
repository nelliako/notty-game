import uuid
from collections import deque
from typing import List

from Class.Classes import Deck, GameState, DrawOptions, Player, PlayerMove, PlayerType, Card
from Logic.utils import handle_action_draw_3, handle_action_steal, handle_action_swap, handle_action_discard_group, \
    all_hands_non_empty, get_permissible_moves
from computerLogic.playerDecision import EASY, MEDIUM, HARD


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
        game_state.players.append(Player(player_id=uuid.uuid4(), hand=[], player_type=PlayerType.COMPUTER_EASY, name=f"Player {i}"))

    # deal 4 cards to each player
    for player in game_state.players:
        player.draw(game_state.deck.draw_cards(4))

    turn = 0
    while all_hands_non_empty(game_state):
        turn += 1
        # events = pygame.event.get()

        # set the current player to the first player and remove current player from the players list
        game_state.current_player = game_state.players.popleft()

        print(f"It's {game_state.current_player.name} turn. It's now turn {turn}.")
        moves = get_permissible_moves(game_state)

        player_moves_map = {
            PlayerType.COMPUTER_EASY: EASY(game_state, moves),
            PlayerType.COMPUTER_MEDIUM: MEDIUM(game_state, moves),
            PlayerType.COMPUTER_HARD: HARD(game_state, moves),
            PlayerType.HUMAN: None,
        }

        computer_player_decision = player_moves_map[game_state.current_player.type]

        if game_state.current_player.type == PlayerType.HUMAN:
            for index in range(len(moves)):
                print(f"{index}: {moves[index]}")
            chosen_move = int(input("Choose your move:"))
            print(f"you chose move: {chosen_move}")
            move = moves[chosen_move]
        else:
            move, _ = player_moves_map[game_state.current_player.type].choose()
            print(f"{game_state.current_player.name} chose move: {move}")

        while True:
            if move == PlayerMove.DRAW:
                handle_action_draw_3(game_state, computer_player_decision)

            if move == PlayerMove.TAKE:
                handle_action_steal(game_state, computer_player_decision)

            if move == PlayerMove.DRAW_ONE:
                handle_action_swap(game_state, computer_player_decision)

            if move == PlayerMove.DISCARD_VALID_CARDS:
                handle_action_discard_group(game_state.current_player, game_state.deck)

            if move == PlayerMove.DRAW or move == PlayerMove.TAKE or move == PlayerMove.DRAW_ONE:
                moves.remove(move)

            if game_state.current_player.type == PlayerType.HUMAN:
                for index in range(len(moves)):
                    print(f"{index}: {moves[index]}")
                chosen_move = int(input("line 96: Choose your move:"))
                print(f"you chose move: {chosen_move}")
                move = moves[chosen_move]
            else:
                move, _ = player_moves_map[game_state.current_player.type].choose()
                print(f"{game_state.current_player.name} chose move: {move}")
                if move == PlayerMove.PASS or move == PlayerMove.END_TURN:
                    break

            if not all_hands_non_empty(game_state):
                break
            
            # END OF MOVE WHILE LOOP

        # add current player to the end of the `players` list
        game_state.players.append(game_state.current_player)

        if not all_hands_non_empty(game_state):
            break
        
        # END OF TURN WHILE LOOP

    if not all_hands_non_empty(game_state):
        for player in game_state.players:
            if len(player.hand) == 0:
                print(f'The winner is {player}')
                # is_endgame = True
                break


