import pygame
import numpy as np
import random


class Dummy():
    def __init__(self,game, current_player, valid_moves):
        self.game = game
        self.current_player = current_player
        self.valid_moves=valid_moves

    def get_random_action(self):
        self.temp=random.choice(self.valid_moves)
        return self.temp
    
    def updateAvailableMoves(self):
        self.valid_moves.remove(self.temp)
        return self.valid_moves
    

    