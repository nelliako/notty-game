import sys
import os
import importlib

from Logic.GameLogic1 import run_game
from Logic.GameLogic import game_loop
from ui.see_screens import see_screens
from ui.see_cards import see_cards

# def test_three_players():
#     import pygame
#     from Logic.Classes import Deck, GameState, PlayerType
#     from ui import screens
#     from collections import deque
#
#     pygame.init()
#     pygame.font.init()
#
#     screen = pygame.display.set_mode((1280, 720))
#     pygame.display.set_caption("Notty Game - 3 Players Test")
#
#     game_state = GameState(players=deque(), deck=Deck())
#     game_state.set_players(3)  # Set to 3 players BEFORE creating playScreen
#     game_state.set_player_difficulty(PlayerType.COMPUTER_EASY)  # Set computer difficulty
#
#     screens.current_screen = screens.playScreen(screen, game_state)
#
#     while screens.current_screen is not None:
#         screens.current_screen.run()
#
#     pygame.quit()
#     sys.exit()

if __name__ == '__main__':
    # Choose one entry point to run by default
    # see_cards()
    # see_screens()
    # run_game()
    # game_loop()

     
