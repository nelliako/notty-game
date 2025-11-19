import pygame
import numpy as np
import random
import PlayerMove


class playerC():
    def __init__(self,deck,players, valid_moves):
        self.deck = deck
        self.curr_player = players[0]
        self.next_player = players[1]
        self.prev_player = players[2]
        self.available_moves=valid_moves


    #creates a array of number of cards in each carrier : Deck, Curr, Next, Prev , Cards in Play
    def observe(self):
        self.game_state = [ len(self.deck), len(self.curr_player.hand), len(next_player.hand), len(prev_player.hand),90 ]
        #following is a sanity check, comment out later , or maybe not
        if sum(self.game_state)!=180: return 'Critical Game Error' #if total number of cards in the game is not 90 at any time

    #creates a weight array that assigns a weight to each card in respective hand 
    def get_weights(self):


    def get_easyMove(self):



    
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