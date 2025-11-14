import pygame
#This class handles the moves the player can make with their cards in the 90 Card game called Notty.

class playerCardMoves:
    def __init__(self, screen, card_images, player_hand, discard_pile,current_deck):
        self.screen = screen
        self.card_images = card_images
        self.player_hand = player_hand
        self.discard_pile = discard_pile
        self.deck = current_deck


    def drawfirstHand(self):
        



    def draw_player_hand(self):
        for index, card in enumerate(self.player_hand):
            card_image = self.card_images[card]
            self.screen.blit(card_image, (50 + index * 100, 400))

    def play_card(self, card_index):
        if 0 <= card_index < len(self.player_hand):
            played_card = self.player_hand.pop(card_index)
            self.discard_pile.append(played_card)
            return played_card
        return None

    def draw_discard_pile(self):
        if self.discard_pile:
            top_card = self.discard_pile[-1]
            card_image = self.card_images[top_card]
            self.screen.blit(card_image, (600, 200))