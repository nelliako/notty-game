import pygame

class visualObject():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, surface):
        pass

class imageObject(visualObject):
    def __init__(self, filename, x, y, position):
        super().__init__(x, y)

        self.image = pygame.image.load(filename).convert_alpha()
        self.size = self.image.get_size()

        self.position = position
        self.update_rect()

    def update_rect(self):
        self.rect = self.image.get_rect()
        if self.position == 'topleft':
            self.rect.topleft = (self.x, self.y)
        elif self.position == 'center':
            self.rect.center = (self.x, self.y)
        elif self.position == 'bottomright':
            self.rect.bottomright = (self.x, self.y)

    def scale(self, new_width, new_height):
        self.image = pygame.transform.scale(self.image, (new_width, new_height))
        self.size = self.image.get_size()


    def draw(self, surface):
        surface.blit(self.image, self.rect)
