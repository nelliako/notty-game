import pygame
from ui.objects import visualObject


class Button(visualObject):
    def __init__(self, image, x_pos, y_pos, text_input, font, on_click = None):
        super().__init__(x_pos, y_pos)
        self.image = image
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.text_input = text_input
        self.font = font
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text = self.font.render(self.text_input, True, 'Black')
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))
        self.on_click = on_click

    def update(self, screen):
        screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        if self.rect.collidepoint(position):
            if self.on_click is not None:
                self.on_click()
            return True
        return False

    def changeColor(self, position):
        if self.rect.collidepoint(position):
            self.text = self.font.render(self.text_input, True, 'White')
        else:
            self.text = self.font.render(self.text_input, True, 'Black')