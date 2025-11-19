import pygame
import numpy as np
import random
import PlayerMove


class playerC():
    def __init__(self, game,deck,players, valid_moves):
        self.hand = hand
        self.game = game
        self.deck = deck
        self.current_player = players[0]
        self.next_player = players[1]
        self.prev_player = players[2]
        self.available_moves=valid_moves


    def observe(self, opp1: PlayerX, opp2: PlayerY):

        playerXHand = opp1.hand
        playerYHand = opp2.hand
        game_state = [ len(self.deck), len(self.hand), len(playerXHand), len(playerYHand), ]
        

    def get_weights(self):




    def get_random_action(self):
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