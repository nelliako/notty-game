import pygame
import sys
from Logic.Classes import Deck, GameState
from ui import screens
from collections import deque



def see_screens():
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Notty Game")

    game_state = GameState(players=deque(), deck=Deck())

    screens.current_screen = screens.menuScreen(screen, game_state)

    while screens.current_screen is not None:
        screens.current_screen.run()

    print("MAIN ENDING")
    pygame.quit()
    sys.exit()



