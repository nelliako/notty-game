import pygame
import numpy as np
import random
import Class.Player from PlayerMove

class Dummy():
    def __init__(self,game,deck,current_player, valid_moves):
        self.game = game
        self.deck = deck
        self.current_player = current_player
        self.valid_moves=valid_moves

    def get_random_move(self):
        self.temp=random.choice(self.valid_moves)
        parameter = random.choice([1,2,3])
        if self.temp == PlayerMove.Draw:
            return (self.temp,parameter)
        
        return (self.temp,0)
    
    def updateAvailableMoves(self):
        self.valid_moves.remove(self.temp)
        return self.valid_moves
            #PlayerMove.DRAW,
            #PlayerMove.TAKE,
            #PlayerMove.DRAW_ONE,
            #PlayerMove.DISCARD_CARD,
            #PlayerMove.DISCARD_VALID_CARDS,
            #PlayerMove.PASS,
            #PlayerMove.END_TURN