import pygame
class CardSprites:
    #loadpngs and store them in a dictionary

    def __init__(self, folder_path="cards"):
        self.cards = {}

        colours = ["red", "green", "yellow", "blue", "black"]
        numbers = range(1, 10)

        for colour in colours:
            for number in numbers:
                filename = f"{colour}_{number}.png"
                path = folder_path + "/" + filename

                image = pygame.image.load(path).convert_alpha()
                self.cards[(colour, number)] = image

        overlay_path = folder_path + "/selected_overlay.png"
        self.overlay = pygame.image.load(overlay_path).convert_alpha()

    def get(self, colour, number):
        return self.cards[(colour, number)]           
    
       
