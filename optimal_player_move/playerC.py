import pygame
import numpy as np
import random

class Dummy():
    def __init__(self,game, current_player, valid_actions):
        self.game = game
        self.current_player = current_player
        self.valid_actions=valid_actions

    def get_random_action(self):
        self.temp=random.choice(self.valid_actions)
        return self.temp
    
    def updateAvailableMoves(self):
        self.valid_actions.remove(self.temp)