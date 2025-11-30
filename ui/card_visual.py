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

        self.overlay = self.sprite_loader.overlay


        self.selected = False
        self.hovered = False

    def draw(self, surface):

        if self.selected:
            draw_y = self.base_y + self.offset_y 
        else:
            draw_y = self.base_y

        surface.blit(self.image, (self.x, draw_y))    
    
        if self.hovered:
            surface.blit(self.overlay, (self.x, draw_y))

    def contains_point(self, mx, my):
        if self.selected:
            check_y = self.base_y + self.offset_y
        else:
            check_y = self.base_y

        return (self.x <= mx <= self.x + self.width and
                check_y <= my <= check_y + self.height)
