#Test Push
#this file contains the core functionalities for playerDecision
# INPUTS: game_state --> An object with properties : players,current_player,chosen_player,deck,state
# OUTPUTS: chosenMove --> A tuple with object playerMove and a parameter of typer integer : (playerMove, parameter)
#                                                           
#                        
import random
from typing import List, Dict
from Logic.Classes import GameState, Player, PlayerMove, Card, CardColor
from Logic.ValidateCardLogic import *

# Base Class for computer_player_decision Players 'EASY', 'MEDIUM' & 'HARD'
class playerDecision:
    def __init__(self, game_state: GameState):
        self.GameState=game_state
        # self.currPlayer=game_state.current_player
        # self.nextPlayer = game_state.players[0]
        # self.prevPlayer = game_state.players[1]
    #delegates to subclasses
    def get_move(self):
        pass

    def choose(self):
        pass

    def choose_number_of_card_to_draw(self, max_allowable_draw) -> int:
        pass

    def choose_player_to_take_from(self) -> int:
        pass

    def choose_card_to_take(self, chosen_player: Player) -> int:
        pass

    def discard_card_from_hand(self) -> int:
        pass

class EASY(playerDecision):
    def __init__(self, game_state: GameState, valid_moves):
        super().__init__(game_state)
        self.game_state = game_state
        self.available_moves = valid_moves
    
    # updates the list of available moves for the current player
    def updateAvailableMoves(self,chosenMove):
        pass
        #removes moves 1,2,3 only as they are only allowed once
        # if chosenMove!=PlayerMove.DISCARD:
        #     self.available_moves.remove(self.temp)
        # return self.available_moves
    
    # core logic for player 'EASY' aka my dearest dummy
    #retrieves and returns a random move from allowed valid moves for the player and also a parameter defining number of cards or chosen player

    def choose(self):
        temp=random.choice(self.available_moves)
        return temp

    def choose_number_of_card_to_draw(self, max_allowable_draw) -> int:
        if max_allowable_draw == 1:
            return 1
        return random.choice(range(1,max_allowable_draw+1))

    def choose_player_to_take_from(self) -> int:
        return random.choice(range(len(self.GameState.players)))

    def choose_card_to_take(self, chosen_player: Player) -> int:
        return random.choice(range(len(chosen_player.hand)))

    def discard_card_from_hand(self) -> int:
        return random.choice(range(len(self.GameState.current_player.hand)))
    
    #returns chosen move and updates latest AvailableMoves
    def get_move(self):
        move=self.choose()
        self.available_moves=self.updateAvailableMoves(move)
        return move



class MEDIUM(playerDecision):
    def __init__(self, game_state: GameState, valid_moves):
        super().__init__(game_state)
        self.game_state = game_state
        self.available_moves = valid_moves
        self.draw_N_value=1
        self.target_player_index=0
    
    def get_discard_group(self):
        valid_group= contains_valid_group(self.game_state.current_player.hand)
        return valid_group

    def numbers_potential(self,cards: List[Card]) -> list[list[Card]] | None:
        number_cards: Dict[int, List[Card]] = {}

        for card in set(cards):
            number = card.number
            if number not in number_cards:
                number_cards[number] = []
                number_cards[number].append(card)
            else:
                number_cards[number].append(card)

        potential_number_groups: List[List[Card]] =[]

        for number in number_cards:
            if len(number_cards[number])<=2:
                potential_number_groups.append(number_cards[number])
        return potential_number_groups
    
    def colors_potential(self, cards: List[Card]) -> list[list[Card]] | None:
        # stores card for each color & number
        colors_cards: Dict[CardColor, Dict[int, Card]] = {}

        for card in set(cards):
            color = card.color
            number = card.number
            if color not in colors_cards:
                colors_cards[color] = {}
            colors_cards[color][number] = card
        
        potential_color_groups: List[List[Card]] = []

        for color in colors_cards:
            numbers = sorted(colors_cards[color].keys())
            if len(numbers) < 2:  # Need at least 2 cards for a potential run
                continue
            
            # Find consecutive runs of length >= 2
            runs = []
            current_run = [numbers[0]]
            
            for i in range(1, len(numbers)):
                if numbers[i] == current_run[-1] + 1:
                    current_run.append(numbers[i])
                else:
                    # Run ended, save if potential (2+)
                    if len(current_run) <= 2:
                        runs.append(current_run[:])
                    current_run = [numbers[i]]
            
            # Check last run
            if len(current_run) <= 2:
                runs.append(current_run)
            
            # Add all potential runs for this color
            for run in runs:
                potential_color_groups.append([colors_cards[color][n] for n in run])
        
        return potential_color_groups
    
    def get_missing_cards(self, type_of_group: str, a_potential_group: List[Card]) -> List[Card] | None:
        if type_of_group=='color':
            if not a_potential_group:
                return None
            group_color = a_potential_group[0].color
            group_numbers = {c.number for c in a_potential_group}
            candidates = set()
            for n in group_numbers:
                if (n - 1) not in group_numbers:
                    candidates.add(n - 1)
                if (n + 1) not in group_numbers:
                    candidates.add(n + 1)
            candidates = {x for x in candidates if 1 <= x <= 9}
            if not candidates:
                return None
            return [Card(group_color, num) for num in sorted(candidates)]

        if type_of_group=='number':
            group_number=a_potential_group[0].number
            group_colors = {c.color for c in a_potential_group}
            all_colors = {CardColor.RED, CardColor.GREEN, CardColor.BLUE, CardColor.BLACK, CardColor.YELLOW}
            missing_colors = list(all_colors - group_colors)
            if not missing_colors:
                return None
            return [Card(color,group_number) for color in missing_colors]
        return None
    
    def get_target_cards(self,hand):
        color_potential_groups,number_potential_groups = self.get_potential_groups(hand)
        target_cards=[]
        for each_group in color_potential_groups:
            missing_cards=self.get_missing_cards('color',each_group)
            if missing_cards:
                target_cards=target_cards+missing_cards
        for each_group in number_potential_groups:
            missing_cards=self.get_missing_cards('number',each_group)
            if missing_cards:
                target_cards=target_cards+missing_cards
        return target_cards
    
    #checks for duplicate cards in hand as that is the most ideal candidate for dumping
    def get_duplicity(self,target: Card, hand: list[Card]) -> int:
        if target is None or not hand:
            return 0
        count= sum(1 for c in hand if c.color == target.color and c.number == target.number)
        return count
    
    def get_potential_groups(self,defined_hand):
        color_potential_groups = self.colors_potential(defined_hand)
        number_potential_groups = self.numbers_potential(defined_hand)
        return [color_potential_groups,number_potential_groups]

    def get_decisionWeights(self,hand):
        color_potential_groups,number_potential_groups = self.get_potential_groups(hand)
        weights: Dict[Card, List[int]] = {}
        non_membership_penalty_factor = 0.3 # arbitrary adjust for performance
        for each_card in hand:
            card_color_weight=0
            card_number_weight=0
            duplicity=0
            for each_group in color_potential_groups:
                if each_card in each_group:
                    card_color_weight+=1 #adds 1 for every color group the card is a member of
                else:
                    card_color_weight-=non_membership_penalty_factor 
            for each_group in number_potential_groups:
                if each_card in each_group:
                    card_number_weight+=1 #adds 1 for every color group the card is a member of
                else:
                    card_number_weight-=non_membership_penalty_factor
            duplicity = self.get_duplicity(each_card,hand)
            weights[each_card] =[card_color_weight,card_number_weight,duplicity]
        return weights

    #TODO: Core logic for player 'MEDIUM'
    def choose(self):
        current_hand = self.game_state.current_player.hand
        valid_group = self.get_discard_group()
        if valid_group!=None:
            move= PlayerMove.DISCARD_VALID_CARDS
        elif len(current_hand)>=17 and PlayerMove.DRAW_ONE in self.available_moves: #17 is arbitrary, can alter to check performance; \\
            # basically prioritises draw 1 and discard 1 when hand volume higher than 17 # TODO: maybe prioritise passing here?
                move = PlayerMove.DRAW_ONE
        else:
            weights=self.get_decisionWeights(current_hand)
            duplicate_cards = any(w[2] > 1 for w in weights.values())
            if duplicate_cards and PlayerMove.DRAW_ONE in self.available_moves:
                move= PlayerMove.DRAW_ONE
            else:
                if self.game_state.number_players==3:
                    target_piles = [self.game_state.players[0].hand,self.game_state.players[1].hand, self.game_state.deck.cards]
                else:
                    target_piles = [self.game_state.players[0].hand, self.game_state.deck.cards]
                probabilities: Dict[Card, tuple[float,int]] = {} # Card -> (best_probability, pile_index)
                for each_target_card in set(self.get_target_cards(current_hand)): #goes through each want to have card for the current existing hand
                    best_prob =0.0
                    best_index = -1
                    for i,pile in enumerate(target_piles):
                        pile_count = len(pile)
                        if each_target_card in pile:
                            instance= sum([ 1 for each_card in pile if each_card==each_target_card])
                            probability_value = instance/ len(pile) 
                            if probability_value> best_prob:
                                best_prob= probability_value
                                best_index = i
                    if best_index >=0:
                        probabilities[each_target_card] = (best_prob,best_index)
                #print('probabilities')
                #print(probabilities)
                if probabilities:
                    best_card, (prob, pile_index) = max(probabilities.items(),key=lambda x:x[1][0])
                    pile_counts = {}
                    for card, (prob,index) in probabilities.items():  # Iterate through all target cards and their pile locations
                        pile_counts[index] = pile_counts.get(index,0)+1


                    deck_index = len(target_piles) - 1
                    deck_size = len(self.game_state.deck.cards)
                    deck_target_card_count = pile_counts.get(deck_index,0)

                    hand_space = 20-len(current_hand)
                    draw_options = []
                    max_draw = min(3,hand_space)
                    for n_draw in range(1, max_draw+1):
                        prob_draw_n = 1 - (((deck_size-deck_target_card_count)/deck_size)**n_draw) #probability of getting a target card from n draws from deck
                        draw_options.append((n_draw,prob_draw_n))
                    
                    player_options = []
                    for index in range(deck_index): # going through 0,1 or 0 only
                        hand_size = len(target_piles[index])
                        if hand_size == 0: return PlayerMove.END_TURN #avoids making any other move when a hand has reached 0
                        if hand_size == 1: continue  # Skip players with only 1 card
                        prob_value_of_index = pile_counts.get(index,0) / hand_size
                        player_options.append((index,prob_value_of_index))
                    if player_options:
                        best_player_index, best_player_prob_value = max (player_options, key=lambda x: x[1])
                    else:
                        best_player_index, best_player_prob_value = (-1,0.0)
                    if draw_options:
                        best_deck_draw_n, best_deck_prob_drawN = max (draw_options, key=lambda x: (x[1],-x[0]))
                    else:
                        best_deck_draw_n, best_deck_prob_drawN = (-1, 0.0)
                    #decide move based on target card concentration in each pile
                    if best_deck_prob_drawN > best_player_prob_value and PlayerMove.DRAW in self.available_moves:
                        move = PlayerMove.DRAW
                        N_options= [n for n,p in draw_options if p>=best_player_prob_value]
                        self.draw_N_value = min(N_options) if N_options else 1
                    elif best_player_prob_value>best_deck_prob_drawN and PlayerMove.TAKE in self.available_moves:
                        move = PlayerMove.TAKE
                        self.target_player_index = best_player_index
                    else:
                        move = PlayerMove.END_TURN #last_possible_move
                        #TODO : create another probability function that basically finds the probability of disrrupting a valid_group/close_to_valid in next_player hand or prev player hand
                        #TODO : disrupt by take one if probability is higher than others?
                else:
                    move = PlayerMove.END_TURN
        self.prev_move = move
        return move
    
    # as per gamelogic, discard_card_from_hand is only \\
    # called when previous move is PlayerMove.DRAW_ONE
    def discard_card_from_hand(self) -> int:
        current_hand=self.game_state.current_player.hand
        weights=self.get_decisionWeights(current_hand)
        duplicate_cards_valuation_factor = 3
        duplicate_cards = [card for card, weight_value in weights.items() if weight_value[2] > 1]
        
        temp = []
        #unpacking the weights dict for ease of use
        for index, each_card in enumerate(current_hand):
            if each_card in weights:
                sum_PG_weights = weights[each_card][0] +weights[each_card][1]
                duplicity = weights[each_card][2]
                temp.append((sum_PG_weights, duplicity, index))

        duplicates= [c for c in temp if (c[1]>1 and c[0]<=duplicate_cards_valuation_factor)]
        
        if duplicates:
            return min(duplicates, key=lambda x: x[0])[2]
        else:
            return min(temp, key=lambda x: x[0])[2] if temp else 0


    # as per gamelogic, choose_player_to_take_from is only \\
    # called when previous move was PlayerMove.TAKE
    def choose_player_to_take_from(self) -> int:
        return self.target_player_index

    def choose_number_of_card_to_draw(self, max_allowable_draw) -> int:
        if max_allowable_draw<self.draw_N_value:
            return max_allowable_draw
        else:
            return self.draw_N_value
    def choose_card_to_take(self, chosen_player: Player) -> int:
        return random.choice(range(len(chosen_player.hand)))
        
#NOT YET IMPLEMENTED
class HARD(playerDecision):
    def __init__(self, game_state: GameState, valid_moves):
        super().__init__(game_state)
        self.game_state = game_state
        self.available_moves = valid_moves

    #TODO: Core logic for player 'HARD'
    def choose(self):
        mcts.get

    #returns single chosen move and calls updateAvailableMoves
    def get_move(self):
        move=self.choose()
        self.available_moves=self.updateAvailableMoves(move)
        return move






    #List of Player Moves for reference
            #PlayerMove.DRAW,
            #PlayerMove.TAKE,
            #PlayerMove.DRAW_ONE,
            #PlayerMove.DISCARD_CARD,
            #PlayerMove.DISCARD_VALID_CARDS,
            #PlayerMove.PASS,
            #PlayerMove.END_TURN