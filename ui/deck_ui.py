import pygame

class Deck:
    def __init__(self, image_surface, x, y, card_back_image):
        self.image = image_surface
        self.card_back = card_back_image
        self.rect = self.image.get_rect(center=(x, y))
        self.animations = []  
        
    def draw_deck(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def start_draw_animation(self, target_x, target_y, speed=10):
        start_x, start_y = self.rect.center
        self.animations.append([start_x, start_y, target_x, target_y, speed])

    def update_and_draw_animations(self, screen):
        new_list = []

        for anim in self.animations:
            x, y, tx, ty, speed = anim

            dx = tx - x
            dy = ty - y
            dist = (dx * dx + dy * dy) ** 0.5

            if dist <= speed:
                continue

            if dist != 0:
                x += speed * (dx / dist)
                y += speed * (dy / dist)

            rect = self.card_back.get_rect()
            rect.center = (int(x), int(y))
            screen.blit(self.card_back, rect.topleft)

            new_list.append([x, y, tx, ty, speed])

        self.animations = new_list
