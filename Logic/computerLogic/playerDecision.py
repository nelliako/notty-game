
#this file contains the core functionalities for playerDecision
# INPUTS: game_state --> An object with properties : players,current_player,chosen_player,deck,state
# OUTPUTS: move --> A move object playerMove , and subsequent methods for associated move actions (which card, which player)
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
    #CALIBRATION CONSTANTS
    POTENTIAL_GROUP_LENGTH = 2 
    COLORS_POTENTIAL_GROUP_LENGTH = POTENTIAL_GROUP_LENGTH # almost valid color group length
    NUMBERS_POTENTIAL_GROUP_LENGTH = POTENTIAL_GROUP_LENGTH +1 #almost valid number .....
    COLOR_MEMBERSHIP_REWARD = 3.14
    NUMBER_MEMBERSHIP_REWARD = 2.58
    NON_MEMBERSHIP_PENALTY = 0.175
    DUPLICATE_RETENTION_VALUATION_FACTOR = 0.43
    MAX_HAND_SIZE = 20
    MIN_HAND_THRESHOLD = 7
    MAX_HAND_THRESHOLD = 17
    LOW_WEIGHT_THRESHOLD = 2
    MOST_USELESS_TO_NUMBER_VALUE=-1.19
    MOST_USELESS_TO_COLOR_VALUE= -1.5

    DEBUG = False
    pause = False
    #DEBUG = True
    #pause = True

    def __init__(self, game_state: GameState,valid_moves):
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
            # Only consider groups with 3+ colors (need 4 for valid, so 3 is "almost there")
            if len(colors)==self.NUMBERS_POTENTIAL_GROUP_LENGTH:
                potential_number_groups.append([numbers_cards[number][c] for c in colors])
        #if self.DEBUG:
            #print()
            #print(potential_number_groups)
            #print()
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
        if self.DEBUG:
            print("#####COLOR POT: ",color_potential_groups)
            print("#####NUMBE POT: ",number_potential_groups)
        return [color_potential_groups,number_potential_groups]

    def get_missing_cards(self, type_of_group: str,a_potential_group: List[Card]) -> List[Card] | None:
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
    def get_duplicity(self,target: Card,hand: list[Card]) -> int:
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
            else:
                card_color_weight=self.MOST_USELESS_TO_COLOR_VALUE
            if number_potential_groups is not None:
                for each_group in number_potential_groups:
                    if each_card in each_group:
                        card_number_weight+=self.NUMBER_MEMBERSHIP_REWARD #adds X for every number group the card is a member of
                    else:
                        card_number_weight-=non_membership_penalty_factor
            else:
                card_number_weight=self.MOST_USELESS_TO_NUMBER_VALUE
            duplicity = self.get_duplicity(each_card,hand)
            weights[each_card] =[card_color_weight,card_number_weight,duplicity]

        return weights  #returns a dict of keys: cards in hand, values:  a list of weights [ color_group_score, number__group_score, instances_of_the_card_]

    #Core logic for player 'MEDIUM'
    def choose(self):
        valid_group= self.get_discard_group() # single valid group
        # init basic valuEs
        current_hand =self.game_state.current_player.hand #getting current cards in current hand : Cards
        hand_size = len(current_hand)
        weights=self.get_decisionWeights(current_hand) # compute and fetch weights for current hand 
        #unpack
        max_color_weight_in_hand,max_number_weight_in_hand, _ = max(weights.values(),key=lambda x:x[0]+x[1]) if weights else [0,0,0]
        max_weight_in_hand= max_color_weight_in_hand+max_number_weight_in_hand # compute a sum of color+number group value
        hand_threshold= (self.MIN_HAND_THRESHOLD if max_weight_in_hand<2 else self.MAX_HAND_THRESHOLD) if weights else self.MAX_HAND_THRESHOLD #arbitrary tuning
        #DEBUG AREA
        if self.DEBUG:
            print("-------current-hand:", len(current_hand)) 
            #print([(card.color.display_name,card.number) for card in current_hand])
            print(weights.values())
            print("-------max weight in hand: ",max_weight_in_hand)
            #print("-------weights: ",weights)
            print("-------valid groups: ",valid_group)
            print()
            print(self.available_moves)
            if valid_group and self.pause: input("Press enter to Continue...")
        #END OF DEBUG AREA

        #DISCARD ALWAYS
        if valid_group!=None:
            return PlayerMove.DISCARD_VALID_CARDS
        

        # main--------------------------------------------

        #hand too big
        if hand_size >= hand_threshold and PlayerMove.DRAW_ONE in self.available_moves: 
            return PlayerMove.DRAW_ONE
        # THIS WAS THE FINAL HITTTTT!!! : SWAP A BIT MORE WHEN HAND MID
        if hand_size<=5 and max_weight_in_hand<=3 and PlayerMove.DRAW_ONE in self.available_moves: 
            return PlayerMove.DRAW_ONE


        #rebuild if hand too small : gets stuck at 1 otherwise
        elif (hand_size<= 4 or max_weight_in_hand<= self.LOW_WEIGHT_THRESHOLD) and PlayerMove.DRAW in self.available_moves:
            if hand_size == 1 or (max_weight_in_hand<(self.LOW_WEIGHT_THRESHOLD-1)):
                self.draw_N_value= 3  # max draw
            elif hand_size<=2 and max_weight_in_hand <=0: # Very weak hand
                self.draw_N_value= 2 
            else:
                self.draw_N_value= 1
            return PlayerMove.DRAW
        
        else:
            #target piles : a list of cards or, piles of card at each stakeholder : each player, deck
            #conditional init of target piles for 3 player or 2 player
            if self.game_state.number_players==3:
                target_piles= [self.game_state.players[0].hand,self.game_state.players[1].hand, self.game_state.deck.cards]
            else:
                target_piles= [self.game_state.players[0].hand, self.game_state.deck.cards]
            
            # edgecase: for some reason gameloop asks for a move even when someone's hand reaches 0 #ask Darron
            opponents_have_cards= any(len(pile) > 0 for pile in target_piles[:-1])  # -1 is deck
            # dict of probability of each target card and their assoc target location index
            probabilities: Dict[Card, tuple[float,int]] = {} # Card -> (best_probability, pile_index)
            for each_target_card in self.get_target_cards(current_hand): #goes through each want to have card for the current existing hand
                best_prob =0.0
                best_index = -1
                for i, pile in enumerate(target_piles):
                    if len(pile) == 0:  # crashed for some cases
                        continue
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
                pile_target_counts = {}
                pile_total_instances = {}
                for card, (prob, pile_index) in probabilities.items():
                    pile_target_counts[pile_index] = pile_target_counts.get(pile_index, 0) + 1
                    pile_size = len(target_piles[pile_index])
                    if pile_size > 0:
                        instances = int(prob * pile_size)
                        pile_total_instances[pile_index] = pile_total_instances.get(pile_index, 0) + instances

                deck_index = len(target_piles) - 1
                deck_size = len(self.game_state.deck.cards)
                hand_space = 20 - hand_size
                player_pile_index = [i for i in pile_target_counts.keys() if i != deck_index]
                draw_options = []
                if deck_index in pile_target_counts and deck_size > 0: 
                    deck_target_count = pile_target_counts[deck_index]  
                    max_draw= min(3, hand_space) 
                       
                    for n_draw in range(1, max_draw + 1):
                        # Probability of getting at least one target card in n draws
                        prob_draw_n= 1 - (((deck_size - deck_target_count) / deck_size) ** n_draw)
                        #weight by concentration ratio
                        deck_concentration= deck_target_count / deck_size
                        weighted_score= prob_draw_n * deck_concentration
                        draw_options.append((n_draw, prob_draw_n, deck_concentration, weighted_score))
                
                # steal from player with higher ratio of targets
                player_options = []
                if opponents_have_cards:
                    for pile_index in player_pile_index:
                        opponent_hand_size = len(target_piles[pile_index])
                        if opponent_hand_size == 0:
                            continue
                        if opponent_hand_size== 1 and hand_size > 3:
                            continue
                        target_count= pile_target_counts.get(pile_index, 0)
                        if target_count>0:
                            #target card to pile count ratio
                            ratio= target_count / opponent_hand_size
                            steal_prob= ratio
                            weighted_score = steal_prob*ratio
                            player_options.append((pile_index, steal_prob, ratio, weighted_score))
                
                best_deck_option= max (draw_options, key=lambda x:x[3]) if draw_options else None
                best_player_option =max(player_options, key=lambda x:x[3]) if player_options else None
                # need to tune more
                endgame_steal_val= 1.5 if hand_size <= 3 else 1.0
                if best_deck_option and best_player_option:
                    deck_score= best_deck_option[3]
                    player_score= best_player_option[3] * endgame_steal_val
                    if deck_score > player_score and PlayerMove.DRAW in self.available_moves: #prioritise deck over player if ratio higher
                        self.draw_N_value = best_deck_option[0]  # n_draw
                        return PlayerMove.DRAW
                    elif PlayerMove.TAKE in self.available_moves: #prioritise playerelse
                        self.target_player_index = best_player_option[0]  # pile_index
                        return PlayerMove.TAKE
                elif best_deck_option and PlayerMove.DRAW in self.available_moves:
                    self.draw_N_value = best_deck_option[0]
                    return PlayerMove.DRAW
                elif best_player_option and PlayerMove.TAKE in self.available_moves:
                    self.target_player_index = best_player_option[0]
                    return PlayerMove.TAKE
            duplicate_cards = any(w[2] > 1 for w in weights.values()) if weights else False
            if duplicate_cards and PlayerMove.DRAW_ONE in self.available_moves:
                return PlayerMove.DRAW_ONE
            if hand_size <= 5 and PlayerMove.DRAW in self.available_moves:
                self.draw_N_value = min(2, 20 - hand_size)
                return PlayerMove.DRAW
            return PlayerMove.END_TURN
        return PlayerMove.PASS
    
    # as per gamelogic, discard_card_from_hand is only \\
    # called when previous move is PlayerMove.DRAW_ONE
    def discard_card_from_hand(self) -> int:
        current_hand=self.game_state.current_player.hand
        weights=self.get_decisionWeights(current_hand)
        duplicate_cards_valuation_factor = self.DUPLICATE_RETENTION_VALUATION_FACTOR
        temp = []
        #unpacking the weights dict
        for index, each_card in enumerate(current_hand):
            if each_card in weights:
                sum_PG_weights = weights[each_card][0] +weights[each_card][1]
                duplicity = weights[each_card][2]
                temp.append((sum_PG_weights, duplicity, index))
        duplicates = [c for c in temp if (c[1]> 1 and c[0]<= duplicate_cards_valuation_factor)]
        if duplicates:
            return min(duplicates, key=lambda x: (x[0], -x[1]))[2]
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
        

class HARD(playerDecision):
    #CALIBRATION CONSTANTS
    POTENTIAL_GROUP_LENGTH = 2 
    COLORS_POTENTIAL_GROUP_LENGTH = POTENTIAL_GROUP_LENGTH # almost valid color group length
    NUMBERS_POTENTIAL_GROUP_LENGTH = POTENTIAL_GROUP_LENGTH +1 #almost valid number .....
    COLOR_MEMBERSHIP_REWARD = 3.14
    NUMBER_MEMBERSHIP_REWARD = 2.58
    NON_MEMBERSHIP_PENALTY = 0.175
    DUPLICATE_RETENTION_VALUATION_FACTOR = 0.43
    MAX_HAND_SIZE = 20
    MIN_HAND_THRESHOLD = 7
    MAX_HAND_THRESHOLD = 17
    LOW_WEIGHT_THRESHOLD = 2
    MOST_USELESS_TO_NUMBER_VALUE=-1.19
    MOST_USELESS_TO_COLOR_VALUE= -1.5

    OPP_LOW_HAND_VALUE=7
    OPP_HIGH_DISCARD_VALUE=3


    DEBUG = False
    pause = False
    #DEBUG = True
    #pause = True

    def __init__(self, game_state: GameState,valid_moves):
        super().__init__(game_state)
        self.game_state = game_state
        self.available_moves = valid_moves
        self.draw_N_value=1
        self.target_player_index=0
    
    def get_discard_group(self,player_hand):
        valid_group= contains_valid_group(player_hand)
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
            # Only consider groups with 3+ colors (need 4 for valid, so 3 is "almost there")
            if len(colors)==self.NUMBERS_POTENTIAL_GROUP_LENGTH:
                potential_number_groups.append([numbers_cards[number][c] for c in colors])
        #if self.DEBUG:
            #print()
            #print(potential_number_groups)
            #print()
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
        if self.DEBUG:
            print("#####COLOR POT: ",color_potential_groups)
            print("#####NUMBE POT: ",number_potential_groups)
        return [color_potential_groups,number_potential_groups]

    def get_missing_cards(self, type_of_group: str,a_potential_group: List[Card]) -> List[Card] | None:
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
    def get_duplicity(self,target: Card,hand: list[Card]) -> int:
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
            else:
                card_color_weight=self.MOST_USELESS_TO_COLOR_VALUE
            if number_potential_groups is not None:
                for each_group in number_potential_groups:
                    if each_card in each_group:
                        card_number_weight+=self.NUMBER_MEMBERSHIP_REWARD #adds X for every number group the card is a member of
                    else:
                        card_number_weight-=non_membership_penalty_factor
            else:
                card_number_weight=self.MOST_USELESS_TO_NUMBER_VALUE
            duplicity = self.get_duplicity(each_card,hand)
            weights[each_card] =[card_color_weight,card_number_weight,duplicity]

        return weights  #returns a dict of keys: cards in hand, values:  a list of weights [ color_group_score, number__group_score, instances_of_the_card_]

    #Core logic for player 'HARD' : MEDIUM + Aggro OFFENSIVE PLAY
    def choose(self):
        # init basic valuEs
        current_hand =self.game_state.current_player.hand #getting current cards in current hand : Cards
        valid_group= self.get_discard_group(current_hand) # single valid group
        
        hand_size = len(current_hand)
        weights=self.get_decisionWeights(current_hand) # compute and fetch weights for current hand 
        #unpack
        max_color_weight_in_hand,max_number_weight_in_hand, _ = max(weights.values(),key=lambda x:x[0]+x[1]) if weights else [0,0,0]
        max_weight_in_hand= max_color_weight_in_hand+max_number_weight_in_hand # compute a sum of color+number group value
        hand_threshold= (self.MIN_HAND_THRESHOLD if max_weight_in_hand<2 else self.MAX_HAND_THRESHOLD) if weights else self.MAX_HAND_THRESHOLD #arbitrary tuning
        
        #target piles : a list of cards or, piles of card at each stakeholder : each player, deck
        #conditional init of target piles for 3 player or 2 player
        if self.game_state.number_players==3:
            target_piles= [self.game_state.players[0].hand,self.game_state.players[1].hand, self.game_state.deck.cards]
            opp_index=[0,1]
        else:
            target_piles= [self.game_state.players[0].hand, self.game_state.deck.cards]
            opp_index=[0]
        deck_index= len(target_piles) -1
        
        
        
                    


        #DEBUG AREA
        if self.DEBUG:
            print("-------current-hand:", len(current_hand)) 
            #print([(card.color.display_name,card.number) for card in current_hand])
            print(weights.values())
            print("-------max weight in hand: ",max_weight_in_hand)
            #print("-------weights: ",weights)
            print("-------valid groups: ",valid_group)
            print()
            print(self.available_moves)
            if valid_group and self.pause: input("Press enter to Continue...")
        #END OF DEBUG AREA

        #DISCARD ALWAYS
        if valid_group!=None:
            return PlayerMove.DISCARD_VALID_CARDS
        

        # main--------------------------------------------

        #hand too big
        if (hand_size >= hand_threshold) and PlayerMove.DRAW_ONE in self.available_moves: 
            return PlayerMove.DRAW_ONE
        # THIS WAS THE FINAL HITTTTT!!! : SWAP A BIT MORE WHEN HAND MID
        if hand_size<=5 and max_weight_in_hand<=3 and PlayerMove.DRAW_ONE in self.available_moves: 
            return PlayerMove.DRAW_ONE

        #rebuild if hand too small : gets stuck at 1 otherwise
        elif (hand_size<= 4 or max_weight_in_hand<= self.LOW_WEIGHT_THRESHOLD) and PlayerMove.DRAW in self.available_moves:
            if (hand_size == 1) or (max_weight_in_hand<(self.LOW_WEIGHT_THRESHOLD-1)):
                self.draw_N_value= 3  # max draw
            elif (hand_size<=2) and (max_weight_in_hand <=0): # Very weak hand
                self.draw_N_value= 2 
            else:
                self.draw_N_value= 1
            return PlayerMove.DRAW
        #steal that hand
        for opp_player_index in opp_index:
            opp_player_hand=target_piles[opp_player_index]
            if len(opp_player_hand)<=self.OPP_LOW_HAND_VALUE and len(opp_player_hand)>1:
                if self.get_discard_group(opp_player_hand) and PlayerMove.TAKE in self.available_moves: #trigger steal
                    return PlayerMove.TAKE 
                elif PlayerMove.TAKE in self.available_moves:
                    player_potential_groups = self.get_potential_groups(opp_player_hand)
                    opp_player_weights = self.get_decisionWeights(opp_player_hand)
                    #weights: Dict[Card, List[int]] = {}
                    opp_max_color_weight_in_hand,opp_max_number_weight_in_hand, _ = max(weights.values(),key=lambda x:x[0]+x[1]) if weights else [0,0,0]
                    opp_max_weight_in_hand= opp_max_color_weight_in_hand+opp_max_number_weight_in_hand # compute a sum of opp color+number group value
                    if opp_max_weight_in_hand>self.OPP_HIGH_DISCARD_VALUE: #trigger steal
                        return PlayerMove.TAKE 


        
        else:
            
            
            # edgecase: for some reason gameloop asks for a move even when someone's hand reaches 0 #ask Darron
            opponents_have_cards= any(len(pile) > 0 for pile in target_piles[:-1])  # -1 is deck
            # dict of probability of each target card and their assoc target location index
            probabilities: Dict[Card, tuple[float,int]] = {} # Card -> (best_probability, pile_index)
            for each_target_card in self.get_target_cards(current_hand): #goes through each want to have card for the current existing hand
                best_prob =0.0
                best_index = -1
                for i, pile in enumerate(target_piles):
                    if len(pile) == 0:  # crashed for some cases
                        continue
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
                
                pile_target_counts = {}
                pile_total_instances = {}
                for card, (prob, pile_index) in probabilities.items():
                    pile_target_counts[pile_index] = pile_target_counts.get(pile_index, 0) + 1
                    pile_size = len(target_piles[pile_index])
                    if pile_size > 0:
                        instances = int(prob * pile_size)
                        pile_total_instances[pile_index] = pile_total_instances.get(pile_index, 0) + instances

                
                deck_size= len(self.game_state.deck.cards)
                hand_space= 20- hand_size
                player_pile_index= [i for i in pile_target_counts.keys() if i != deck_index]
                draw_options = []
                if deck_index in pile_target_counts and deck_size > 0: 
                    deck_target_count = pile_target_counts[deck_index]  
                    max_draw= min(3, hand_space) 
                       
                    for n_draw in range(1, max_draw + 1):
                        # Probability of getting at least one target card in n draws
                        prob_draw_n= 1 - (((deck_size - deck_target_count) / deck_size) ** n_draw)
                        #weight by concentration ratio
                        deck_concentration= deck_target_count / deck_size
                        weighted_score= prob_draw_n * deck_concentration
                        draw_options.append((n_draw, prob_draw_n, deck_concentration, weighted_score))
                
                # steal from player with higher ratio of targets
                player_options = []
                if opponents_have_cards:
                    for pile_index in player_pile_index:
                        opponent_hand_size = len(target_piles[pile_index])
                        if opponent_hand_size == 0:
                            continue
                        if opponent_hand_size== 1 and hand_size > 3:
                            continue
                        target_count= pile_target_counts.get(pile_index, 0)
                        if target_count>0:
                            #target card to pile count ratio
                            ratio= target_count / opponent_hand_size
                            steal_prob= ratio
                            weighted_score = steal_prob*ratio
                            player_options.append((pile_index, steal_prob, ratio, weighted_score))
                
                best_deck_option= max (draw_options, key=lambda x:x[3]) if draw_options else None
                best_player_option =max(player_options, key=lambda x:x[3]) if player_options else None
                # need to tune more
                endgame_steal_val= 1.5 if hand_size <= 3 else 1.0
                if best_deck_option and best_player_option:
                    deck_score= best_deck_option[3]
                    player_score= best_player_option[3] * endgame_steal_val
                    if deck_score > player_score and PlayerMove.DRAW in self.available_moves: #prioritise deck over player if ratio higher
                        self.draw_N_value = best_deck_option[0]  # n_draw
                        return PlayerMove.DRAW
                    elif PlayerMove.TAKE in self.available_moves: #prioritise playerelse
                        self.target_player_index = best_player_option[0]  # pile_index
                        return PlayerMove.TAKE
                elif best_deck_option and PlayerMove.DRAW in self.available_moves:
                    self.draw_N_value = best_deck_option[0]
                    return PlayerMove.DRAW
                elif best_player_option and PlayerMove.TAKE in self.available_moves:
                    self.target_player_index = best_player_option[0]
                    return PlayerMove.TAKE
            duplicate_cards = any(w[2] > 1 for w in weights.values()) if weights else False
            if duplicate_cards and PlayerMove.DRAW_ONE in self.available_moves:
                return PlayerMove.DRAW_ONE
            if hand_size <= 5 and PlayerMove.DRAW in self.available_moves:
                self.draw_N_value = min(2, 20 - hand_size)
                return PlayerMove.DRAW
            return PlayerMove.END_TURN
        return PlayerMove.PASS
    
    # as per gamelogic, discard_card_from_hand is only \\
    # called when previous move is PlayerMove.DRAW_ONE
    def discard_card_from_hand(self) -> int:
        current_hand=self.game_state.current_player.hand
        weights=self.get_decisionWeights(current_hand)
        duplicate_cards_valuation_factor = self.DUPLICATE_RETENTION_VALUATION_FACTOR
        temp = []
        #unpacking the weights dict
        for index, each_card in enumerate(current_hand):
            if each_card in weights:
                sum_PG_weights = weights[each_card][0] +weights[each_card][1]
                duplicity = weights[each_card][2]
                temp.append((sum_PG_weights, duplicity, index))
        duplicates = [c for c in temp if (c[1]> 1 and c[0]<= duplicate_cards_valuation_factor)]
        if duplicates:
            return min(duplicates, key=lambda x: (x[0], -x[1]))[2]
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