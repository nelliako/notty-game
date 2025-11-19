import pygame
import numpy as np
import random
import PlayerMove

class Dummy():
    def __init__(self,game,deck,current_player, valid_moves):
        self.game = game
        self.deck = deck
        self.current_player = current_player
        self.valid_moves=valid_moves
    #retrieves and returns a random move from allowed valid moves for the player and also a parameter defining number of cards
    def get_random_move(self):
        self.temp=random.choice(self.valid_moves)
        parameter = random.choice([1,2,3])
        if self.temp == PlayerMove.Draw:
            return (self.temp,parameter)
        
        return (self.temp,0)
    # updates the list of available moves for the current player
    def updateAvailableMoves(self):
        #removes moves 1,2,3 only as they are only allowed once
        if self.temp!=PlayerMove.DISCARD_VALID_CARDS or self.temp!=PlayerMove.PASS or self.temp!=PlayerMove.END_TURN:
            self.valid_moves.remove(self.temp)
        return self.valid_moves
    
    #List of Player Moves for reference
            #PlayerMove.DRAW,
            #PlayerMove.TAKE,
            #PlayerMove.DRAW_ONE,
            #PlayerMove.DISCARD_CARD,
            #PlayerMove.DISCARD_VALID_CARDS,
            #PlayerMove.PASS,
            #PlayerMove.END_TURN