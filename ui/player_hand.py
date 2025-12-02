import pygame

class PlayerHand:
    def __init__(self, center_x, center_y, spacing, orientation):
        
        self.center_x = center_x
        self.center_y = center_y
        self.spacing = spacing
        self.orientation = orientation
        self.cards = []

    def add_card(self, card):
      
        if self.orientation == "vertical":
            rot_angle = -90
            card.image = pygame.transform.rotate(card.image, rot_angle)
            card.rect = card.image.get_rect()
           
            if getattr(card, 'overlay', None) is not None:
                card.overlay = pygame.transform.rotate(card.overlay, rot_angle)
            card.width = card.image.get_width()
            card.height = card.image.get_height()
       
        setattr(card, 'hand_orientation', self.orientation)
        self.cards.append(card)
        self.update_positions()

    def clear(self):
        self.cards = []

    def update_positions(self):
        if not self.cards:
            return

        count = len(self.cards)

        if self.orientation == "horizontal":
           
            total_width = self.spacing * (count - 1)
            start_x = self.center_x - total_width / 2
            y = self.center_y

            for i, card in enumerate(self.cards):
                card.x = int(start_x + i * self.spacing)
                card.base_y = int(y)
                card.update_position()

        else:
           
            v_spacing = -self.spacing
            total_height = v_spacing * (count - 1)
            start_y = self.center_y - total_height / 2
            x = self.center_x

            for i, card in enumerate(self.cards):
                card.x = int(x)
                card.base_y = int(start_y + i * v_spacing)
                card.update_position()

    def draw(self, surface):
        for card in self.cards:
            card.draw(surface)
