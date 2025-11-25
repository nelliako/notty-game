import uuid
from collections import deque

from Class.Classes import PlayerType, Player, Deck, GameState
from Logic.utils import handle_action_draw_3, handle_action_steal, handle_action_swap, handle_action_discard_group, \
    all_hands_non_empty, get_permissible_moves, TurnContext
from computerLogic.playerDecision import EASY, MEDIUM, HARD

def run_game():
    # Initialise Players
    players = deque()
    for i in range(game_state.number_players):
        players.append(Player(image=None, x=0, y=0, player_id=uuid.uuid4(), hand=[], player_type=PlayerType.HUMAN, name=f"Player {i}"))

    # 1. Setup
    game_state = GameState(players=players, deck=Deck())

    # Deal Hands 
    for player in game_state.players:
        player.draw(game_state.deck.draw_cards(4))

    print("Game Start")
    turn_context = TurnContext()

    # Passing turns from player to player
    while True:

        game_state.current_player = game_state.players.popleft()

        moves = get_permissible_moves(game_state)

        player_moves_map = {
            PlayerType.COMPUTER_EASY: EASY(game_state, moves),
            PlayerType.COMPUTER_MEDIUM: MEDIUM(game_state, moves),
            PlayerType.COMPUTER_HARD: HARD(game_state, moves),
            PlayerType.HUMAN: None,
        }

        # Resetting flags 
        turn_context.reset()
        opponents = game_state.players

        computer_player_decision = player_moves_map[game_state.current_player.type]

        # ACTION PHASE MENU
        user_input = 0
        # While there is no winner -> while all hands are not empty
        while all_hands_non_empty(game_state) and (user_input != 5 and user_input != 6):
            # Show the state to the user - current player, their hand and other players' hands
            print(f"current player: {game_state.current_player.type}, hand {game_state.current_player.hand}")
            for player in opponents:
                print(f"opponent: {player.type}, hand {player.hand}")

            
            # If none of the actions with constraints have been exhausted
            if turn_context.has_drawn_cards == False and turn_context.has_stolen_card == False and turn_context.has_swapped_card == False:
                user_input = int(input('Choose your action - 1: Draw cards 2: Steal 3: Draw and Discard 4: Discard 5: Pass 6: End turn\n'))

            elif turn_context.has_drawn_cards == True and turn_context.has_stolen_card == False and turn_context.has_swapped_card == False:
                user_input = int(input('Choose your action - 2: Steal 3: Draw and Discard 4: Discard 5: Pass 6: End turn\n'))
            
            elif turn_context.has_drawn_cards == True and turn_context.has_stolen_card == False and turn_context.has_swapped_card == True:
                user_input = int(input('Choose your action - 2: Steal 4: Discard 5: Pass 6: End turn\n'))

            elif turn_context.has_drawn_cards == False and turn_context.has_stolen_card == True and turn_context.has_swapped_card == False:
                user_input = int(input('Choose your action - 1: Draw cards 3: Draw and Discard 4: Discard 5: Pass 6: End turn\n'))

            elif turn_context.has_drawn_cards == False and turn_context.has_stolen_card == False and turn_context.has_swapped_card == True:
                user_input = int(input('Choose your action - 1: Draw cards 2: Steal 4: Discard 5: Pass 6: End turn\n'))

            elif turn_context.has_drawn_cards == True and turn_context.has_stolen_card == True and turn_context.has_swapped_card == False:
                user_input = int(input('Choose your action - 3: Draw and Discard 4: Discard 5: Pass 6: End turn\n'))

            elif turn_context.has_drawn_cards == False and turn_context.has_stolen_card == True and turn_context.has_swapped_card == True:
                user_input = int(input('Choose your action - 1: Draw cards 4: Discard 5: Pass 6: End turn\n'))
            # If all of the actions with constraints have been exhausted    
            elif turn_context.has_drawn_cards == True and turn_context.has_stolen_card == True and turn_context.has_swapped_card == True:
                user_input = int(input('Choose your action - 4: Discard 5: Pass 6: End turn\n'))


            # TAKING ACTIONS ACCORDING TO INPUT
        
            if user_input == 1:
                handle_action_draw_3(game_state, computer_player_decision, turn_context)
                # Go back to the action phase menu
            if user_input == 2:
                handle_action_steal(game_state, computer_player_decision, turn_context)

            if user_input == 3:
                handle_action_swap(game_state, computer_player_decision, turn_context)

            if user_input == 4:
                handle_action_discard_group(game_state.current_player, game_state.deck, turn_context)
                    # checking the win
                    # returning to the action phase
        # Check whose hand is exactly non empty and announce the winner
        is_endgame = False
        if not all_hands_non_empty(game_state):
            for player in game_state.players:
                if len(player.hand) == 0:
                    print(f'The winner is {player}')
                    is_endgame = True
                    break
        if is_endgame:
            break
        # Adding current_player back to the deck on the right
        game_state.players.append(game_state.current_player)
