#Test Push
#this file contains the core functionalities for playerDecision
# INPUTS: game_state --> An object with properties : players,current_player,chosen_player,deck,state
# OUTPUTS: chosenMove --> A tuple with object playerMove and a parameter of typer integer : (playerMove, parameter)
#                                                           
#                        
import random

from Logic.Classes import GameState, Player, PlayerMove

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
    
    # core logic for player 'EASY' aka my dummy
    #retrieves and returns a random move from allowed valid moves for the player and also a parameter defining number of cards or chosen player
    def choose(self):
        temp=random.choice(self.available_moves)
        # Note  : Parameter defines number of cards for DRAW-N and defines playerNumber for  TAKE
        if temp == PlayerMove.DRAW or temp ==PlayerMove.TAKE:
            parameter = random.choice([1,2,3])
            return temp, parameter
        elif temp == PlayerMove.TAKE:
            parameter = random.choice([0,1])   #assuming deque 'players' in gamestate has the remaining 2 players with indices 0,1
            return temp, parameter

        return temp,0

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
    
    # updates the list of available moves for the current player
    def updateAvailableMoves(self,chosenMove):
        #removes moves 1,2,3 only as they are only allowed once
        if chosenMove!=PlayerMove.DISCARD:
            self.available_moves.remove(self.temp)
        return self.available_moves
    
    #TODO: Core logic for player 'MEDIUM'
    def choose(self):
        pass

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