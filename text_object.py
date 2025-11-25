import pygame
from ui.objects import visualObject

class textObject(visualObject):
    def __init__(self, x, y, text, font_path, font_size, color, position='center'):
        super().__init__(x, y)
        self.text = text
        self.font_path = font_path
        self.font_size = font_size
        self.color = color
        self.position = position

        #private variable
        self._font = pygame.font.Font(self.font_path, self.font_size)
        self.render()

    def text_content(self, new_text):
        if self.text != new_text:
            self.text = new_text
            self.render()

    def font_size(self, new_size):
        if self.font_size != new_size:
            self.font_size = new_size
            self._font = pygame.font.Font(self.font_path, self.font_size)
            self.render()

    def update_rect(self):
        self.rect = self.surf.get_rect()
        if self.position == 'topleft':
            self.rect.topleft = (self.x, self.y)
        elif self.position == 'center':
            self.rect.center = (self.x, self.y)
        elif self.position == 'bottomright':
            self.rect.bottomright = (self.x, self.y)

    def render(self):
        self.surf = self._font.render(self.text, True, self.color)
        self.update_rect()

    def draw(self, screen):
        screen.blit(self.surf, self.rect)