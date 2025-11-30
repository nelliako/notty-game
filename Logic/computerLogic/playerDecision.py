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
    def updateAvailableMoves(self,chosenMove):
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
        return random.choice(range(1,max_allowable_draw))

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
        self.drawedOne = False
        self.discardCandidates=[]
    
    # updates the list of available moves for the current player
    def updateAvailableMoves(self,chosenMove):
        #removes moves 1,2,3 only as they are only allowed once
        if chosenMove!=PlayerMove.DISCARD:
            self.available_moves.remove(self.temp)
        return self.available_moves
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
            potential_number_groups.append(number_cards[number])
        return potential_number_groups
    
    def colors_potential(self, cards: List[Card]) -> list[list[Card]] | None:
        
        # number of cards per color
        colors = {}
        # stores card for each color & number
        colors_cards: Dict[CardColor, Dict[int, Card]] = {}

        for card in set(cards):
            color = card.color
            number = card.number

            if color not in colors_cards:
                colors[color] = 1
                colors_cards[color] = {}
            else:
                colors[color] = colors[color] + 1

            if not colors_cards[color].get(number, False):
                colors_cards[color][number] = card
            else:
                colors_cards[color][number] = card

                #edit alter
        potential_color_groups:List[List[Card]] =[]

        for color in colors_cards:
            keys = sorted(list(colors_cards[color].keys()))
            consecutive_numbers = 0
            for i in range(len(keys)):
                if (keys[i] + 1) in keys:
                    consecutive_numbers += 1
            if consecutive_numbers <= 2:
                potential_color_groups.append( [colors_cards[color][number] for number in colors_cards[color]])

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
            target_cards=target_cards+self.get_missing_cards('color',each_group)
        for each_group in number_potential_groups:
            target_cards=target_cards+self.get_missing_cards('number',each_group)
        return target_cards
    
    #checks for duplicate cards in hand as that is the most ideal candidate for dumping
    def get_duplicity(target: Card, hand: list[Card]) -> int:
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
        for each_card in hand:
            card_color_weight=0
            card_number_weight=0
            duplicity=0
            for each_group in color_potential_groups:
                if each_card in each_group:
                    card_color_weight+=1 #adds 1 for every color group the card is a member of
                else:
                    card_color_weight-=1 #subtracts 1 for every color group  the card is not a member of
            for each_group in number_potential_groups:
                if each_card in each_group:
                    card_number_weight+=1 #adds 1 for every color group the card is a member of
                else:
                    card_number_weight-=1 #subtracts 1 for every color group  the card is not a member of
            duplicity = self.get_duplicity(each_card,hand)
            weights[each_card] =[card_color_weight,card_number_weight,duplicity]
        return weights
    def update_discardCandidates(self,listOfCard):
        self.discardCandidates= self.discardCandidates + listOfCard
        self.discardCandidates=list(set(list(self.discardCandidates))) #filters and removes more than 1 instance in discardable pile
    #TODO: Core logic for player 'MEDIUM'
    def choose(self):
        
        current_hand = self.game_state.current_player.hand
        valid_group = self.get_discard_group()

        if valid_group!=None:
            move= PlayerMove.DISCARD_VALID_CARDS
        elif len(current_hand)>=17: #17 is arbitrary, can alter to check performance; \\
            # basically prioritises draw 1 and discard 1 when hand volume higher than 17 # TODO: maybe prioritise passing here?
            move = PlayerMove.DRAW_ONE
        else:
            weights=self.get_decisionWeights(current_hand)
            duplicate_cards =any([weight_value[2] > 1] for card, weight_value in weights.items())
            if duplicate_cards:
                move= PlayerMove.DRAW_ONE
            else:
                for card,weight_value in weights.items():
                    pass
                    # TO DO : generate probability of receiving target_cards using card weights from deck | opp1 | opp2

                move = PlayerMove.END_TURN #last_possible_move

        #remaining = DRAW_ONE, DRAW, TAKE
        self.prev_move = move
        return move
    
    # as per gamelogic, discard_card_from_hand is only \\
    # called when previous move was PlayerMove.DRAW_ONE
    def discard_card_from_hand(self) -> int:
        current_hand=self.game_state.current_player.hand
        weights=self.get_decisionWeights(current_hand)
        duplicate_cards = [card for card, weight_value in weights.items() if weight_value[2] > 1]
        discardCandidates=list(set(list(duplicate_cards))) #filters and removes more than 1 instance in discardABLE pile
        chosenDiscardCard=random.choice(self.discardCandidates)
        #TODO: if chosenDiscardCard in HV_groups and weight==3 or more, choose least weighed card
        return chosenDiscardCard
    
    #returns single chosen move and calls updateAvailableMoves
    def get_move(self):
        move=self.choose()
        self.available_moves=self.updateAvailableMoves(move)
        return move

class HARD(playerDecision):
    def __init__(self, game_state: GameState, valid_moves):
        super().__init__(game_state)
        self.game_state = game_state
        self.available_moves = valid_moves
    
    # updates the list of available moves for the current player
    def updateAvailableMoves(self,chosenMove):
        #removes moves 1,2,3 only as they are only allowed once
        if chosenMove!=PlayerMove.DISCARD:
            self.available_moves.remove(self.temp)
        return self.available_moves
    
    




    #TODO: Core logic for player 'HARD'
    def choose(self):
        pass

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