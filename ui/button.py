import pygame
import pygame

from ui.objects import visualObject


class Button(visualObject):
    def __init__(self, image, x_pos, y_pos, text_input, font, on_click):
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
        self.normal_image = image
        self.selected_image = None
        self.is_selected = False

    def update(self, screen):
        if self.is_selected and self.selected_image is not None:
            self.image = self.selected_image
        else:
            self.image = self.normal_image
        screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def handle_event(self, event):
        if self.rect.collidepoint(event.pos):
            print(f"mouse event position: {event.pos}")
            if self.on_click is not None:
                print("button pressed")
                return self.on_click()

    def changeColor(self, position):
        if self.rect.collidepoint(position):
            self.text = self.font.render(self.text_input, True, 'White')
        else:
            self.text = self.font.render(self.text_input, True, 'Black')