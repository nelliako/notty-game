import pygame
import numpy as np
import random
import PlayerMove

class Dummy():
    def __init__(self,current_player, valid_moves):
        self.current_player = current_player
        self.available_moves=valid_moves
    
    # updates the list of available moves for the current player
    def updateAvailableMoves(self):
        #removes moves 1,2,3 only as they are only allowed once
        if self.temp!=PlayerMove.DISCARD_VALID_CARDS or self.temp!=PlayerMove.PASS or self.temp!=PlayerMove.END_TURN:
            self.available_moves.remove(self.temp)
        return self.available_moves
    
    #retrieves and returns a random move from allowed valid moves for the player and also a parameter defining number of cards
    def get_random_move(self):
        self.temp=random.choice(self.available_moves)
        parameter = random.choice([1,2,3])
        self.available_moves=self.updateAvailableMoves()
        if self.temp == PlayerMove.Draw:
            return (self.temp,parameter)
        return (self.temp,0)
    
    #List of Player Moves for reference
            #PlayerMove.DRAW,
            #PlayerMove.TAKE,
            #PlayerMove.DRAW_ONE,
            #PlayerMove.DISCARD_CARD,
            #PlayerMove.DISCARD_VALID_CARDS,
            #PlayerMove.PASS,
            #PlayerMove.END_TURN