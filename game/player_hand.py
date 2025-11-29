class PlayerHand:
    def __init__(self, center_x, center_y, spacing, orientation):
        self.center_x = center_x
        self.center_y = center_y
        self.spacing = spacing
        self.orientation = orientation
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)
        self.update_positions()

    def remove_card(self, card):
        self.cards.remove(card)
        self.update_positions()

    def update_positions(self):
        if len(self.cards) == 0:
            return

        count = len(self.cards)
        spacing = self.spacing
        total_width = (count - 1) * abs(spacing)

        if self.orientation == "horizontal":
            # horizontally centered around center_x
            start_x = self.center_x - total_width // 2
            y = self.center_y

            for i, card in enumerate(self.cards):
                card.x = start_x + (i * spacing)
                card.base_y = y

        else:
            start_y = self.center_y - total_width // 2
            x = self.center_x

    def draw(self, surface):
        for card in self.cards:
            card.draw(surface)
