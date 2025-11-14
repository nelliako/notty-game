import pygame
import numpy as np
import random



class RandomPlayerTurn:
    def __init__(self, game, current_player, valid_moves):
        self.game = game
        self.current_player = current_player


    def get_move(self):
        valid_moves = self.game.get_valid_moves(self.current_player)
        move = random.choice(valid_moves)
        return move
    
    def make_move(self):
        move = self.get_move()
        self.game.make_move(move, self.current_player)
        return self.game
    
    def get_turn_moves(self):
        valid_moves = self.game.get_valid_moves(self.current_player)

        


        return valid_moves