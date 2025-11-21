import pygame
import numpy as np
import random
import PlayerMove


class playerC():
    def __init__(self,deck,players, valid_moves):
        self.deck = deck
        self.players=players
        self.curr_player = players[0]
        self.next_player = players[1]
        self.prev_player = players[2]
        self.available_moves=valid_moves
    # updates the list of available moves for the current player
    def updateAvailableMoves(self):
        #removes moves 1,2,3 only as they are only allowed once
        if self.temp!=PlayerMove.DISCARD_VALID_CARDS or self.temp!=PlayerMove.PASS or self.temp!=PlayerMove.END_TURN:
            self.available_moves.remove(self.temp)
        return self.available_moves
    #creates a array of number of cards in each carrier : Deck, Curr, Next, Prev , Cards in Play
    def observe(self):
        self.game_state = [ len(self.deck), len(self.curr_player.hand), len(self.next_player.hand), len(self.prev_player.hand),90 ]
        #following is a sanity check, comment out later , or maybe not
        if sum(self.game_state)!=180: return 'Critical Game Error' #if total number of cards in the game is not 90 at any time

    #creates a weight array that assigns a weight to each card in respective hand defining card worth in possible groups
    def get_weights(self):
        x=[]
        for each_player in self.players:
            temp_groupsA= each_player.hand.get_possibleAGroups()
            temp_groupsB= each_player.hand.get_possibleBGroups()
            for each_card in self.curr_player.hand:
                A=0
                B=0
                for each_group in temp_groupsA:
                    if each_card in each_group:
                        A+=1
                for each_group in temp_groupsB:
                    if each_card in each_group:
                        B+=1
                
                x.append([each_card,(A,B)])
                


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