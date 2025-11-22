import random
import sys
import uuid
from typing import List, Optional
from collections import deque
from Class.Classes import Deck, GameState, State, DrawOptions, Player, PlayerMove, PlayerType
from Class.Classes import PlayerType, Player, Deck, GameState, Card, create_deck, CardColor
from Logic.ValidateCardLogic import contains_valid_group

# Turns Tracking: tracks the state of the current turn to enforce "at most per turn" rules
class TurnContext:

    def __init__(self):
        self.has_drawn_cards = False      # Action 1
        self.has_stolen_card = False      # Action 2
        self.has_swapped_card = False     # Action 3

    def reset(self):
        self.has_drawn_cards = False
        self.has_stolen_card = False
        self.has_swapped_card = False

# Action Handlers 

# Action 1: draw up to 3 cards, constraint - cannot exceed 20 cards in hand & can be done once per turn
def handle_action_draw_3(player: Player, deck: Deck, context: TurnContext):
   
    # Calculate max cards player can draw without exceeding 20
    space_in_hand = 20 - len(player.hand)
    max_draw = min(3, space_in_hand)

    if max_draw <= 0:
        print('Hand is full! Cannot draw.')
        return

    # Determine how many to draw 
    # For Computer: deciding randomly; for Human: input
    if player.type == PlayerType.COMPUTER:
        count = random.randint(1, max_draw)
    else:
        try:
            user_input = int(input(f'Draw how many cards? (1-{max_draw}): '))
            count = max(1, min(user_input, max_draw)) # i.e. if user input is 99 and they are allowed to draw 3, this will default to 3
        except ValueError:
            count = 1 # Default to 1 card on error

    cards = deck.draw_cards(count)
    player.draw(cards)
    print(f"Player drew {len(cards)} cards.")
    
    # Mark this action as done for this turn
    context.has_drawn_cards = True


#  Action 2: Steal a random card from an opponent; constraint - cannot exceed 20 cards in hand, can be done once per turn
def handle_action_steal(current_player: Player, opponents: List[Player], context: TurnContext):
  
    if len(current_player.hand) >= 20:
        print('Hand full, cannot steal.')
        return

    # Filter opponents who actually have cards
    valid_targets = [p for p in opponents if len(p.hand) > 0]
    
    if not valid_targets:
        print('No opponents have cards to steal!')
        return None

    # Select target
    # TODO: prompt current player to choose the user BUT leave this line for a computer player type
    target: Player = random.choice(valid_targets)
    
    # Select Random Card from Target (mimics shuffling hand face down)
    card_index = random.randint(0, len(target.hand) - 1)
    stolen_card = target.lose_card(card_index)
    
    current_player.take_card(stolen_card)
    print(f'Stole a card from Player {target.player_id}')
    
    context.has_stolen_card = True

    # Check if the opponent won (ran out of cards due to steal) 
    # This will be caught in the main loop win check

# Action 3: draw 1 card, discard 1 card; constraints
def handle_action_swap(player: Player, deck: Deck, context: TurnContext):

    # Has this action been done before?
    if context.has_swapped_card == True:
        return

    # Drawing card from the deck and accessing it from the list
    card_drawn = deck.draw_cards(1)[0]
    print(f'You drew {card_drawn}')

    # Choose the card to discard when player is human

    if player.type == PlayerType.HUMAN:
        print('Which card do you want to discard?')

        # Numerating the cards so that the user could choose which one to discard
        for card in range(len(player.hand)):
            print(card)
            print (player.hand[card])
        print(len(player.hand))
        print(card_drawn)
        user_input = int(input('Provide the card number'))

        # Discard the chosen card
        if user_input == len(player.hand):
            context.has_swapped_card = True
            deck.add_cards([card_drawn])
            deck.shuffle_deck()
            return

        player.take_card(card_drawn)
        player.lose_card(user_input)
        # Adding the removed card back to the deck
        deck.add_cards([player.hand[user_input]])
        # Shuffling the deck 
        deck.shuffle_deck()
        context.has_swapped_card = True
        return
    
    # Choose the card to discard when player is computer
    if player.type == PlayerType.COMPUTER: 
        # Pick a random card
        # [0, len(player.hand) - 1] indices correspond to the current hand
        # len(player.hand) index in the drawn_card.
        card_index = random.randint(0, len(player.hand))
        # If we choose the drawn_card, the hand does not change
        if card_index != len(player.hand):
            player.lose_card(card_index)
            player.take_card(card_drawn)
        # Adding the removed card back to the deck
        deck.add_cards([player.hand[card_index]])
        # Shuffling the deck 
        deck.shuffle_deck()
        context.has_swapped_card = True
        return


# Actions 4: discard group - no constraints
def handle_action_discard_group(player: Player, deck: Deck, context: TurnContext):
    valid_group = contains_valid_group(player.hand)
    if valid_group is not None:
        for card in valid_group:
            for index in range(len(player.hand)):
                if card == player.hand[index]:
                    #player.discard_valid_cards(list())
                    # Adding the removed card back to the deck
                    deck.add_cards(player.discard_valid_cards(list()))
                    # Shuffling the deck 
                    deck.shuffle_deck()
                    break


# Checking for the while condition
def all_hands_non_empty(state: GameState):
    for player in state.players:
        if len(player.hand) == 0:
            return False

    return True

# Main game loop
def run_game():

    # Initialise Players
    players = deque()
    num_players = 3
    for _ in range(num_players):
        players.append(Player(image=None, x=0, y=0, player_id=uuid.uuid4(), hand=[], player_type=PlayerType.HUMAN))

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
        # Resetting flags 
        turn_context.reset()
        opponents = game_state.players 

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
            
                handle_action_draw_3(game_state.current_player, game_state.deck, turn_context)
                # Go back to the action phase menu
            if user_input == 2:
                handle_action_steal(game_state.current_player, opponents, turn_context)

            if user_input == 3:
                handle_action_swap(game_state.current_player, game_state.deck, turn_context)

            if user_input == 4:
                handle_action_discard_group(game_state.current_player, game_state.deck, turn_context)
                    # checking the win
                    # returning to the action phase
        # Check whose hand is exactly non empty and announce the winner
        is_endgame = False
        if all_hands_non_empty(game_state) == False:
            for player in game_state.players:
                if len(player.hand) == 0:
                    print(f'The winner is {player}')
                    is_endgame = True
                    break
        if is_endgame:
            break
        # Adding current_player back to the deck on the right
        game_state.players.append(game_state.current_player)








