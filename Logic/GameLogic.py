import uuid
from collections import deque
from typing import List

from Logic.Classes import Deck, GameState, DrawOptions, Player, PlayerMove, PlayerType, Card
from Logic.utils import handle_action_draw_3, handle_action_steal, handle_action_swap, handle_action_discard_group, \
    all_hands_non_empty, get_permissible_moves
from Logic.computerLogic.playerDecision import EASY, MEDIUM, HARD


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
    game_state.deck.shuffle_deck(trigger_ui=False)  

    
    game_state.players.append(Player(player_id=uuid.uuid4(), hand=[], player_type=PlayerType.COMPUTER_EASY, name=f"Player {0}"))
    game_state.players.append(Player(player_id=uuid.uuid4(), hand=[], player_type=PlayerType.COMPUTER_EASY, name=f"Player {1}"))
    game_state.players.append(Player(player_id=uuid.uuid4(), hand=[], player_type=PlayerType.COMPUTER_EASY, name=f"Player {2}"))

    # deal 4 cards to each player
    for player in game_state.players:
        player.draw(game_state.deck.draw_cards(4))

    turn = 0
    while all_hands_non_empty(game_state):
        turn += 1
        # events = pygame.event.get()

        # set the current player to the first player and remove current player from the players list
        game_state.current_player = game_state.players.popleft()
        print('------------------------------------------------')#Optional Output Print for ease of read : remove for final
        print(f"It's {game_state.current_player.name} turn. It's now turn {turn}.")
        moves = get_permissible_moves(game_state)
        print('------------------------------------------------')#Optional Output Print for ease of read : remove for final
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
            move = player_moves_map[game_state.current_player.type].choose() #calling to playerDecision
            print(f"{game_state.current_player.name} chose move: {move}")

        while True:
            print(f"Game State Deck size: {len(game_state.deck.cards)}")

            total_cards = list(game_state.deck.cards)
            for player in [game_state.current_player] + list(game_state.players):
                print(f"{player.name}'s hand size: {len(player.hand)}!")
                total_cards += list(player.hand)

            print(f"Total Cards: {len(total_cards)}")

            if len(total_cards) > 90:
                seen_ids = set()
                unique_cards = []

                for card in total_cards:
                    if card.id not in seen_ids:
                        unique_cards.append(card)
                        seen_ids.add(card.id)

                print(unique_cards)
                print(seen_ids)
                raise ValueError("Cards in deck exceeds 90 cards!")

            print(
                f"Game state Current Player {game_state.current_player.name} Hand Size: {len(game_state.current_player.hand)}")
            if len(game_state.current_player.hand) > 20:
                raise ValueError(f"{game_state.current_player.name}'s hand exceeds 20 cards!")



            if move == PlayerMove.DRAW:
                handle_action_draw_3(game_state, computer_player_decision)

            if move == PlayerMove.TAKE:
                handle_action_steal(game_state, computer_player_decision)

            if move == PlayerMove.DRAW_ONE:
                handle_action_swap(game_state, computer_player_decision)

            if move == PlayerMove.DISCARD_VALID_CARDS:
                handle_action_discard_group(game_state)

            if move == PlayerMove.DRAW or move == PlayerMove.TAKE or move == PlayerMove.DRAW_ONE:
                moves.remove(move)

            if game_state.current_player.type == PlayerType.HUMAN:
                for index in range(len(moves)):
                    print(f"{index}: {moves[index]}")
                chosen_move = int(input("line 96: Choose your move:"))
                print(f"you chose move: {chosen_move}")
                move = moves[chosen_move]
            else:
                move = player_moves_map[game_state.current_player.type].choose()
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
                print(f'The winner is {player.name}')
                # is_endgame = True
                break


