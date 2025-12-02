import pygame

class CardVisual:
    def __init__(self, colour, number, sprite_loader):
        self.colour = colour
        self.number = number

       
        self.sprite_loader = sprite_loader
        self.image = sprite_loader.get(colour, number)

  
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.x = 0
        self.base_y = 0
       
        self.offset_y = -20  
        self.offset_x = 20  
       
        self.hand_orientation = "horizontal"
      
        self.overlay = getattr(self.sprite_loader, "overlay", None)

        self.selected = False
        self.hovered = False

        self.rect = pygame.Rect(self.x, self.base_y, self.width, self.height)

    def update_position(self):
        
        if self.selected and self.hand_orientation == "vertical":
            draw_x = self.x + self.offset_x
            draw_y = self.base_y
        else:
            draw_x = self.x
            draw_y = self.base_y + (self.offset_y if self.selected else 0)
        self.rect.topleft = (draw_x, draw_y)

    def draw(self, surface):
        
        if self.selected and self.hand_orientation == "vertical":
            draw_x = self.x + self.offset_x
            draw_y = self.base_y
        else:
            draw_x = self.x
            draw_y = self.base_y + (self.offset_y if self.selected else 0)
        self.rect.topleft = (draw_x, draw_y)
        surface.blit(self.image, (draw_x, draw_y))
        if (self.hovered or self.selected) and self.overlay:
            surface.blit(self.overlay, (draw_x, draw_y))

    def contains_point(self, mx, my):
        return self.rect.collidepoint(mx, my)
