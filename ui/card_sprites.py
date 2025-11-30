import pygame
import os


class CardSprites:
    # loadpngs and store them in a dictionary

    def __init__(self, folder_name="cardsImages"):
        self.cards = {}

        base_path = os.path.dirname(__file__)
        full_folder_path = os.path.join(base_path, folder_name)

        colours = ["red", "green", "yellow", "blue", "black"]
        numbers = range(1, 10)

        for colour in colours:
            for number in numbers:
                filename = f"{colour}_{number}.png"
                path = os.path.join(full_folder_path, filename)

                try:
                    image = pygame.image.load(path).convert_alpha()
                    self.cards[(colour, number)] = image
                except FileNotFoundError:
                    print(f"Error: Could not find image at {path}")

        overlay_path = os.path.join(full_folder_path, "selected_overlay.png")
        try:
            self.overlay = pygame.image.load(overlay_path).convert_alpha()
        except FileNotFoundError:
            print(f"Error: could not find overlay at {overlay_path}")

    def get(self, colour, number):
        return self.cards[(colour, number)]
