from optparse import Option

import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Button test")
main_font = pygame.font.Font("ui/Font/Minecraftia-Regular.ttf", 20)
background_surf = pygame.image.load("ui/images/Vector.png").convert_alpha()
title_font = pygame.font.Font("ui/Font/Minecraftia-Regular.ttf", 250)
title_surf = title_font.render("NOTTY", True, 'Black')
title_rect = title_surf.get_rect(center = (640, 220))



class Button():
    def __init__(self, image, x_pos, y_pos, text_input):
        self.image = image
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.text_input = text_input
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text = main_font.render(self.text_input, True, 'Black')
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self):
        screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    # check mouse position x, y
    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            print("Button Pressed")

    def changeColor(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            self.text = main_font.render(self.text_input, True, 'White')
        else:
            self.text = main_font.render(self.text_input, True, 'Black')

button_surf = pygame.image.load("ui/buttonImages/orangeButton.png").convert_alpha()
button_surf = pygame.transform.scale(button_surf, (200, 50))

play_button = Button(button_surf, 640, 450, "Play")
Options_button = Button(button_surf, 640, 530, "Options")
Exit_button = Button(button_surf, 640, 610, "Exit")

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            play_button.checkForInput(pygame.mouse.get_pos())
            Options_button.checkForInput(pygame.mouse.get_pos())
            Exit_button.checkForInput(pygame.mouse.get_pos())

    screen.fill((212, 212, 212))
    screen.blit(background_surf, (0, 0))

    screen.blit(title_surf, title_rect)

    play_button.update()
    play_button.changeColor(pygame.mouse.get_pos())

    Options_button.update()
    Options_button.changeColor(pygame.mouse.get_pos())

    Exit_button.update()
    Exit_button.changeColor(pygame.mouse.get_pos())

    pygame.display.update()


