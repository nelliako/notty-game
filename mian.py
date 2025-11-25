import pygame
import sys

pygame.init()
pygame.font.init()
from ui import screens


screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Notty Game")


def run_game():
    screens.current_screen = screens.menuScreen(screen)

    while screens.current_screen is not None:
        screens.current_screen.run()

    print("MAIN ENDING")
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run_game()


