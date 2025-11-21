#this file contains the core functionalities for playerDecision
# INPUTS: GameState --> An object with properties : players,currentPlayer,chosenPlayer,deck,state
# OUTPUTS: chosenMove --> An object with properties : move, a integer parameter for move (drawn N, Steal from N player)\
#                                                           currentplayer making the move
#                        
import pygame
import random
from Class.Classes import Deck, GameState, State, DrawOptions
from Class.Player import Player, PlayerMove, PlayerType

class chosenMove:
    def __init__(self,currPlayer,outMove,intParam):
        self.currPlayer = currPlayer
        self.move = outMove
        self.intParam = intParam

# Base Class for computer Players 'EASY', 'MEDIUM' & 'HARD'
class playerDecision:
    def __init__(self, GameState):
        self.GameState=GameState
        self.currPlayer=GameState.currentPlayer
        self.nextPlayer = GameState.players[0]
        self.prevPlayer = GameState.players[1]
    
    def get_move(self):
        pass


class EASY(playerDecision):
    def __init__(self,valid_moves):
        super().__init__(GameState)
        self.available_moves=valid_moves
        self.available_moves=valid_moves
    
    # updates the list of available moves for the current player
    def updateAvailableMoves(self,chosenMove):
        #removes moves 1,2,3 only as they are only allowed once
        if chosenMove!=PlayerMove.DISCARD:
            self.available_moves.remove(self.temp)
        return self.available_moves
    
    #retrieves and returns a random move from allowed valid moves for the player and also a parameter defining number of cards or chosen player
    def choose(self):
        self.temp=random.choice(self.available_moves)
        # Note  : Parameter defines number of cards for DRAW-N and defines playerNumber for  TAKE
        if self.temp == PlayerMove.DRAW or self.temp ==PlayerMove.TAKE:
            parameter = random.choice([1,2,3])
            return (self.temp,parameter)
        elif self.temp ==PlayerMove.TAKE:
            parameter = random.choice([0,1])   #assuming deque 'players' in gamestate has the remaining 2 players with indices 0,1
            return (self.temp,parameter) 
        return (self.temp,0)

    #returns chosen move and updates latest AvailableMoves
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