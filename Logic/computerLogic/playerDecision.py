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
from Logic.computerLogic.mcts import *

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
    POTENTIAL_GROUP_LENGTH = 2
    COLORS_POTENTIAL_GROUP_LENGTH = POTENTIAL_GROUP_LENGTH
    NUMBERS_POTENTIAL_GROUP_LENGTH = POTENTIAL_GROUP_LENGTH +1
    COLOR_MEMBERSHIP_REWARD = 2
    NUMBER_MEMBERSHIP_REWARD = 2
    NON_MEMBERSHIP_PENALTY = 0.05
    DUPLICATE_RETENTION_VALUATION_FACTOR = 0.5
    MAX_HAND_SIZE = 20
    MIN_HAND_THRESHOLD = 6
    MAX_HAND_THRESHOLD = 16
    LOW_WEIGHT_THRESHOLD = 2
    CARD_NUMBER_MIN = 1
    CARD_NUMBER_MAX = 9
    MOST_USELESS_TO_NUMBER_VALUE=-100
    MOST_USELESS_TO_COLOR_VALUE= -100

    DEBUG = True

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
        #finds all possible potential groups of same number but 4 different colors 
        numbers_cards: Dict[int, Dict[CardColor, Card]] = {}
        for card in set(cards): #for each unique card in hand
            color = card.color      #getting the color
            number = card.number    #getting the number
            if number not in numbers_cards: # if the number isnt a key in the dict, 
                numbers_cards[number] = {} #initing the number as a key in the outer dict
            numbers_cards[number][color] = card #inserting the card as an entry in the inner dict under the number key of outer dict
        potential_number_groups: List[List[Card]] =[]
        for number in numbers_cards: #going through each entry in outer dict
            colors = list(numbers_cards[number].keys()) # under a entry, getting the list of different colors under the current entry
            if len(colors)>=self.NUMBERS_POTENTIAL_GROUP_LENGTH:
                potential_number_groups.append([numbers_cards[number][c] for c in colors])
        print()
        print(potential_number_groups)
        print()
        return potential_number_groups if potential_number_groups else None
    
    def colors_potential(self, cards: List[Card]) -> list[list[Card]] | None: 
        #finds all possible potential groups of same color but 2 consecutive numbers , or 2 numbers separated by 1 missing card
        # cards : current hand
        
        colors_cards: Dict[CardColor, Dict[int, Card]] = {} # a dictionary where key: CardColor value : (a dict with key: int value: the card itself)

        for card in set(cards): #for each unique card in hand
            color = card.color      #getting the color
            number = card.number    #getting the number
            if color not in colors_cards: # if the color isnt a key in the dict, 
                colors_cards[color] = {} #initing the color as a key in the outer dict
            colors_cards[color][number] = card #inserting the card as an entry in the inner dict under the color key of outer dict
        
        potential_color_groups: List[List[Card]] = []

        for color in colors_cards: #going through each entry in outer dict
            numbers = sorted(colors_cards[color].keys()) # under a entry, getting the list of numbers under the current entry
            if len(numbers) < self.COLORS_POTENTIAL_GROUP_LENGTH:  # Need at least 2 cards for a potential group run
                continue
            
            # Find consecutive runs of length >= 2
            runs = []
            current_run = [numbers[0]]
            
            for i in range(1, len(numbers)):
                if numbers[i] == current_run[-1] + 1 or numbers[i] == current_run[-1] + 2:
                    current_run.append(numbers[i]) #save the next entry to current_run if its a direct consecutive or the last of a consecutive 3 series
                else:   # Run ended, save if potential group is (2+)
                    if len(current_run) >= self.COLORS_POTENTIAL_GROUP_LENGTH: #if the run so far is 2+, save it
                        runs.append(current_run[:]) #saving all saved in current_run
                    current_run = [numbers[i]]  #resets current_run starting point to the breakpoint
            
            # Check last run
            if len(current_run) >= self.COLORS_POTENTIAL_GROUP_LENGTH:
                runs.append(current_run)
            
            # Add all potential runs for this color to the final output list
            for run in runs:
                potential_color_groups.append([colors_cards[color][n] for n in run]) #extracts the card object from the inner dict for the respective number n
        
        return potential_color_groups if potential_color_groups else None
    
    def get_potential_groups(self,defined_hand):
        color_potential_groups = self.colors_potential(defined_hand) # valid length is 3
        number_potential_groups = self.numbers_potential(defined_hand) #plus 1 because valid group is length 4
        return [color_potential_groups,number_potential_groups]

    def get_missing_cards(self, type_of_group: str, a_potential_group: List[Card]) -> List[Card] | None:
        if type_of_group=='color':
            if not a_potential_group:
                return None
            group_color = a_potential_group[0].color
            group_numbers = {c.number for c in a_potential_group}
            candidates = set()
            # if group length is varied, will need to updated this segment to go through all inbetweens 
            for n in sorted(group_numbers):
                if(n+2) in group_numbers: #checks if the group type is inbetweener
                    return [Card(group_color, n+1)] # directly returns the inbetweener missing card , not adjacents
                else:
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
        if color_potential_groups is not None:
            for each_group in color_potential_groups:
                missing_cards=self.get_missing_cards('color',each_group)
                if missing_cards:
                    target_cards=target_cards+missing_cards
        if number_potential_groups is not None:
            for each_group in number_potential_groups:
                missing_cards=self.get_missing_cards('number',each_group)
                if missing_cards:
                    target_cards=target_cards+missing_cards
        return list(set(target_cards))
    
    #checks for duplicate cards in hand as that is the most ideal candidate for dumping
    def get_duplicity(self,target: Card, hand: list[Card]) -> int:
        if target is None or not hand:
            return 0
        count= sum(1 for c in hand if c.color == target.color and c.number == target.number)
        return count
    
    # WEIGHT CALCULATIONS FOR CARDS IN A HAND
    def get_decisionWeights(self,hand):
        color_potential_groups,number_potential_groups = self.get_potential_groups(hand)
        weights: Dict[Card, List[int]] = {}
        non_membership_penalty_factor = self.NON_MEMBERSHIP_PENALTY # arbitrary adjust for performance
        for each_card in hand:
            card_color_weight=0
            card_number_weight=0
            duplicity=0
            if color_potential_groups is not None:
                for each_group in color_potential_groups:
                    if each_card in each_group:
                        card_color_weight+=self.COLOR_MEMBERSHIP_REWARD #adds X for every color group the card is a member of
                    else:
                        card_color_weight-=non_membership_penalty_factor
            #else:
                #card_color_weight=self.MOST_USELESS_TO_COLOR_VALUE
            if number_potential_groups is not None:
                for each_group in number_potential_groups:
                    if each_card in each_group:
                        card_number_weight+=self.NUMBER_MEMBERSHIP_REWARD #adds X for every number group the card is a member of
                    else:
                        card_number_weight-=non_membership_penalty_factor
            #else:
                #card_color_weight=self.MOST_USELESS_TO_NUMBER_VALUE
            duplicity = self.get_duplicity(each_card,hand)
            weights[each_card] =[card_color_weight,card_number_weight,duplicity]

        return weights  #returns a dict of keys: cards in hand, values:  a list of weights [ color_group_score, number__group_score, instances_of_the_card_]

    #TODO: Core logic for player 'MEDIUM'
    def choose(self):
        valid_group = self.get_discard_group() # Get list of a single Valid Group in current hand 
         # IMMEDIATELY RETURN DISCARD A GROUP MOVE WHEN FOUND
        if valid_group!=None:
            return PlayerMove.DISCARD_VALID_CARDS
        
        # INIT SOME VALUES
        current_hand = self.game_state.current_player.hand #getting current cards in current hand : Cards
        weights=self.get_decisionWeights(current_hand) # compute and fetch weights for current hand 
        # unpack weights to get maximum color_group_value and maximum_number_group_value of the card that has it; 
        max_color_weight_in_hand,max_number_weight_in_hand,_= max(weights.values(),key=lambda x:x[0]+x[1]) if weights else [0,0,0]
        max_weight_in_hand = max_color_weight_in_hand+max_number_weight_in_hand # compute a sum of color+number group value
        hand_threshold = (12 if max_weight_in_hand<2 else 17) if weights else 17 #arbitrary tuning

        #DEBUG AREA
        if self.DEBUG:
            print("-------current-hand:", len(current_hand)) 
            print([(card.color.display_name,card.number) for card in current_hand])
            print(weights.values())
            print("-------max weight in hand: ",max_weight_in_hand)
            #print("-------weights: ",weights)
            print("-------valid groups: ",valid_group)
            if valid_group: input("Press enter to Continue...")
        #END OF DEBUG AREA

        # MAIN BLOCK

        #IF HAND IS TOO BIG : REDUCE HAND BY JUST DRAWING 1 and DISCARDING LEAST VALUABLE CARD
        if len(current_hand)>=hand_threshold and PlayerMove.DRAW_ONE in self.available_moves: 
            return PlayerMove.DRAW_ONE

        #REBUILD HAND if its low but very weak
        elif (len(current_hand)<=4 or max_weight_in_hand<=2) and PlayerMove.DRAW in self.available_moves:
            self.draw_N_value= 3 if len(current_hand)==1 else 1 # maximize hand size when only 1 card left for an end game
            return PlayerMove.DRAW
        
        else:
            #target piles : a list of cards or, piles of card at each stakeholder : each player, deck
            #conditional init of target piles for 3 player or 2 player
            if self.game_state.number_players==3:
                target_piles = [self.game_state.players[0].hand,self.game_state.players[1].hand, self.game_state.deck.cards]
            else:
                target_piles = [self.game_state.players[0].hand, self.game_state.deck.cards]
            # building a probability dict for computing probability of getting a target card
            probabilities: Dict[Card, tuple[float,int]] = {} # Card -> (best_probability, pile_index)
            for each_target_card in self.get_target_cards(current_hand): #goes through each want to have card for the current existing hand
                best_prob =0.0
                best_index = -1
                for i,pile in enumerate(target_piles):
                    if each_target_card in pile:
                        instance= sum( 1 for each_card in pile if each_card==each_target_card)
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
                    N_options= [n for n,p in draw_options if p>=best_player_prob_value]
                    self.draw_N_value = min(N_options) if N_options else 1
                    return PlayerMove.DRAW
                elif best_player_prob_value>best_deck_prob_drawN and PlayerMove.TAKE in self.available_moves:
                    self.target_player_index = best_player_index
                    return PlayerMove.TAKE

            duplicate_cards = any(w[2] > 1 for w in weights.values())
            if duplicate_cards and PlayerMove.DRAW_ONE in self.available_moves:
                return PlayerMove.DRAW_ONE
            else:
                return PlayerMove.END_TURN

        return PlayerMove.PASS
    # as per gamelogic, discard_card_from_hand is only \\
    # called when previous move is PlayerMove.DRAW_ONE
    def discard_card_from_hand(self) -> int:
        current_hand=self.game_state.current_player.hand
        weights=self.get_decisionWeights(current_hand)
        duplicate_cards_valuation_factor = self.DUPLICATE_RETENTION_VALUATION_FACTOR
        
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
        mcts = MonteCarlo(self.game_state,self.available_moves)
        mcts.get_optimal_move()

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