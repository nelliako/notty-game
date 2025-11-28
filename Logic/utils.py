from typing import List

from Class.Classes import PlayerType, Player, Deck, GameState, PlayerMove
from Logic.ValidateCardLogic import contains_valid_group
from computerLogic.playerDecision import playerDecision, HARD, MEDIUM, EASY


# Turns Tracking: tracks the state of the current turn to enforce "at most per turn" rules
class TurnContext:

    def __init__(self):
        self.has_drawn_cards = False  # Action 1
        self.has_stolen_card = False  # Action 2
        self.has_swapped_card = False  # Action 3

    def reset(self):
        self.has_drawn_cards = False
        self.has_stolen_card = False
        self.has_swapped_card = False


# Action Handlers

# Action 1: draw up to 3 cards, constraint - cannot exceed 20 cards in hand & can be done once per turn

def handle_action_draw_3(game_state: GameState, computer_player: playerDecision, TurnContext: TurnContext = None, ui_callback = None):
    number_of_cards = 0
    # Calculate max cards player can draw without exceeding 20
    space_in_hand = 20 - len(game_state.current_player.hand)
    max_draw = min(3, space_in_hand)

    if max_draw <= 0:
        print('Hand is full! Cannot draw.')
        return

    # Determine how many to draw
    # For Computer: deciding randomly; for Human: input
    if game_state.current_player.type == PlayerType.HUMAN and not game_state.computer_playing_for_human:
        if ui_callback:
            ui_callback(max_draw)
        else:
            user_input = int(input(f'You can draw between 1 and {max_draw} cards: '))
            number_of_cards = max(1, min(user_input,
                                         max_draw))  # i.e. if user input is 99 and they are allowed to draw 3, this will default to 3
            game_state.current_player.draw(game_state.deck.draw_cards(number_of_cards=number_of_cards))
    else:
        if (len(game_state.current_player.hand) + max_draw) <= 20:
            number_of_cards = computer_player.choose_number_of_card_to_draw(max_draw)
            game_state.current_player.draw(game_state.deck.draw_cards(number_of_cards=number_of_cards))


#  Action 2: Steal a random card from an opponent; constraint - cannot exceed 20 cards in hand, can be done once per turn
def handle_action_steal(game_state: GameState, computer_player_decision: playerDecision, context: TurnContext = None):
    chosen_card = None
    if len(game_state.current_player.hand) >= 20:
        print('Hand full, cannot steal.')
        return

    # Filter opponents who actually have cards
    valid_targets = [p for p in game_state.players if len(p.hand) > 0]

    if not valid_targets:
        print('No opponents have cards to steal!')
        return

    # Select target
    # TODO: prompt current player to choose the user BUT leave this line for a computer_player_decision player type

    if game_state.current_player.type == PlayerType.HUMAN and not game_state.computer_playing_for_human:
        while chosen_card is None:
            while game_state.chosen_player is None:
                for index, player in enumerate(game_state.players):
                    print(f'{index}: {player.name}')
                    # player.update(events)
                    if player.is_selected:
                        game_state.chosen_player = player
                        game_state.chosen_player.shuffle_hand()

                chosen_player = int(input("Choose which player to steal a card from:"))
                game_state.chosen_player = game_state.players[chosen_player]
                game_state.chosen_player.shuffle_hand()

                chosen_card = int(input(f"Choose which card to steal (enter a number from 0 to {len(game_state.chosen_player.hand)-1}):"))
                break

            while game_state.chosen_player is not None and chosen_card is None:
                for card in game_state.chosen_player.hand:
                    # card.update(events)
                    if card.is_selected:
                        chosen_card = game_state.chosen_player.hand.index(card)


    else:
        # target: Player = random.choice(valid_targets)
        game_state.chosen_player = game_state.players[
            computer_player_decision.choose_player_to_take_from()]

        game_state.chosen_player.shuffle_hand()

        # Select Random Card from Target (mimics shuffling hand face down)
        # card_index = random.randint(0, len(target.hand) - 1)
        chosen_card = computer_player_decision.choose_card_to_take(game_state.chosen_player)

    print(f'Stole a card from {game_state.chosen_player.name}')

    # Check if the opponent won (ran out of cards due to steal)
    # This will be caught in the main loop win check

    # stolen_card = target.lose_card(card_index)
    stolen_card = game_state.chosen_player.lose_card(chosen_card)
    game_state.current_player.take_card(stolen_card)

    game_state.chosen_player = None


# Action 3: draw 1 card, discard 1 card; constraints
def handle_action_swap(game_state: GameState, computer_player_decision: playerDecision = None,
                       context: TurnContext = None):
    # Has this action been done before?
    if context is not None and context.has_swapped_card:
        return

    # Drawing card from the deck and accessing it from the list
    card_drawn = game_state.deck.draw_cards(1)[0]
    print(f'You drew {card_drawn}')

    # add drawn card to player hand
    game_state.current_player.take_card(card_drawn)

    # Choose the card to discard when player is human

    if game_state.current_player.type == PlayerType.HUMAN and not game_state.computer_playing_for_human:
        print('Which card do you want to discard?')

        # Numerating the cards so that the user could choose which one to discard
        for card in range(len(game_state.current_player.hand)):
            print(card)
            print(game_state.current_player.hand[card])
        print(len(game_state.current_player.hand))
        print(card_drawn)

        # choose which card to discard
        card_to_be_discarded = int(input('Provide the card number'))

        # Discard the chosen card
        discarded_card = game_state.current_player.lose_card(card_to_be_discarded)
        # Adding the removed card back to the deck
        game_state.deck.add_cards([discarded_card])
        # Shuffling the deck
        game_state.deck.shuffle_deck()
        context.has_swapped_card = True
        return

    # Choose the card to discard when player is computer
    elif computer_player_decision is not None:
        # choose which card to discard
        card_to_be_discarded = computer_player_decision.discard_card_from_hand()
        # Discard the chosen card
        discarded_card = game_state.current_player.lose_card(card_to_be_discarded)

        # Adding the removed card back to the deck
        game_state.deck.add_cards([discarded_card])
        # Shuffling the deck
        game_state.deck.shuffle_deck()
        if context is not None:
            context.has_swapped_card = True
        return


# Actions 4: discard group - no constraints
def handle_action_discard_group(game_state: GameState, context: TurnContext = None):
    valid_group = []
    if game_state.current_player.type != PlayerType.HUMAN and not game_state.computer_playing_for_human:
        valid_group = contains_valid_group(game_state.current_player.hand)
        if valid_group is not None:
            # player.discard_valid_cards(list())
            # Adding the removed card back to the deck
            game_state.current_player.discard_valid_cards(valid_group)
            game_state.deck.add_cards(valid_group)
            # Shuffling the deck
            game_state.deck.shuffle_deck()
            return True
        return False
    else:
        # while contains_valid_group(selected_cards) is None:
        #     for card in game_state.current_player.hand:
        # card.update(events)

        # selected_cards = [card for card in game_state.current_player.hand if card.is_selected]
        # if contains_valid_group(selected_cards) is None:
        #     print("Selected cards must be a valid group.")
        valid_group = contains_valid_group(game_state.current_player.hand)
        if valid_group is not None:
            game_state.current_player.discard_valid_cards(valid_group)
            game_state.deck.add_cards(valid_group)
            game_state.deck.shuffle_deck()
            return True
        return False


# Checking for the while condition
def all_hands_non_empty(state: GameState):
    temp_list = list(state.players) + [state.current_player] if state.current_player is not None else list(
        state.players)

    for player in temp_list:
        if len(player.hand) == 0:
            return False

    return True

def get_permissible_moves(game_state: GameState) -> list[PlayerMove]:
    available_moves: List[PlayerMove] = [
        PlayerMove.DRAW,
        PlayerMove.TAKE,
        PlayerMove.DRAW_ONE,
        # PlayerMove.DISCARD_CARD,
        PlayerMove.DISCARD_VALID_CARDS,
        PlayerMove.PASS,
        PlayerMove.END_TURN
    ]

    restricted_moves: List[PlayerMove] = [
        # PlayerMove.DISCARD_CARD,
        PlayerMove.DISCARD_VALID_CARDS,
        PlayerMove.PASS,
        PlayerMove.END_TURN
    ]

    moves: List[PlayerMove] = available_moves if len(game_state.current_player.hand) < 20 else restricted_moves
    return moves


def get_computer_player_decision(game_state, moves: list[PlayerMove]):
    player_moves_map = {
        PlayerType.COMPUTER_EASY: EASY(game_state, moves),
        PlayerType.COMPUTER_MEDIUM: MEDIUM(game_state, moves),
        PlayerType.COMPUTER_HARD: HARD(game_state, moves),
        PlayerType.HUMAN: None,
    }

    return player_moves_map[game_state.current_player.type]