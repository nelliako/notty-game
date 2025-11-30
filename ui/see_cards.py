import pygame
from ui.card_sprites import CardSprites
from ui.card_visual import CardVisual
from ui.player_hand import PlayerHand

def see_cards():
    pygame.init()

    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Notty UI Test")

    sprites = CardSprites("cardsImages")

    hand = PlayerHand(700, 70, -40, "horizontal")

    card1 = CardVisual("red", 5, sprites)
    card2 = CardVisual("blue", 3, sprites)
    card3 = CardVisual("yellow", 8, sprites)
    card4 = CardVisual("green", 2, sprites)

    hand.add_card(card1)
    hand.add_card(card2)
    hand.add_card(card3)
    hand.add_card(card4)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()

                for card in hand.cards:
                    if card.contains_point(mx, my):

                        if card.selected == False:
                            card.selected = True
                        else:
                            card.selected = False

            mx, my = pygame.mouse.get_pos()
            for card in hand.cards:
                card.hovered = card.contains_point(mx, my)

        screen.fill((30, 30, 30))        

        for card in hand.cards:
                card.draw(screen)
        

        pygame.display.flip()
    

    pygame.quit()

    # run_game()
    # game_loop()

