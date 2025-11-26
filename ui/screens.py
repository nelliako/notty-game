import pygame
import sys
import uuid
from collections import deque
from ui.button import Button
from ui.objects import imageObject
from ui.text_object import textObject
from Class.Classes import PlayerType, Player, Deck, GameState, CardColor
from cards.card_sprites import CardSprites
from visuals.card_visual import CardVisual
from game.player_hand import PlayerHand
from Logic.utils import TurnContext, handle_action_draw_3, handle_action_steal, handle_action_swap, handle_action_discard_group

current_screen = None

class screenBase():
    def __init__(self, screen):
        self.screen = screen
        self.close = False

    def process_event(self, event):
        pass

    def update_objects(self):
        pass

    def draw_objects(self):
        pass

    def run(self):
        global current_screen
        clock = pygame.time.Clock()

        while not self.close:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    current_screen = None
                    self.close = True
                    print("QUIT EVENT")

                    pygame.quit()
                    sys.exit()
                    return

                self.process_event(event)

            if self.close:
                print("LEAVING RUN()")
                return

            self.update_objects()
            self.draw_objects()
            pygame.display.update()
            clock.tick(60)


class menuScreen(screenBase):
    def __init__(self, screen, game_state):
        super().__init__(screen)
        self.game_state = game_state

        self.title = textObject(640, 220, "NOTTY", "ui/Font/Minecraftia-Regular.ttf", 250, 'Black', 'center')

        self.background_surf = pygame.image.load("ui/images/Vector.png").convert_alpha()

        button_surf = pygame.image.load("ui/buttonImages/orangeButton.png").convert_alpha()
        button_surf = pygame.transform.scale(button_surf, (200, 50))

        button_font = pygame.font.Font("ui/Font/Minecraftia-Regular.ttf", 20)
        self.play_button = Button(button_surf, 640, 450, "Play", button_font, self.navigate_to_play_screen)
        self.options_button = Button(button_surf, 640, 530, "Options", button_font, self.navigate_to_options_screen)
        self.exit_button = Button(button_surf, 640, 610, "Exit", button_font, self.navigate_to_exit_screen)

    def process_event(self, event):
        global current_screen
        # if event.type == pygame.MOUSEBUTTONDOWN:
        # checkForInput
        # click_pos = event.pos

        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in [self.play_button, self.options_button, self.exit_button]:
                if button.rect.collidepoint(event.pos):
                    screen = button.handle_event(event)
                    if screen is not None:
                        current_screen = screen
                        print(f"current screen:  {current_screen}")
                        self.close = True
                        return


            # current_screen = playScreen(self.screen, self.game_state)
            # self.close = True
            # return

            # if self.options_button.handle_event(click_pos):
            #     current_screen = OptionSelectScreen(self.screen, self.game_state)
            #     self.close = True
            #     return
            #
            # if self.exit_button.handle_event(click_pos):
            #     print("EXIT CLICKED")
            #     self.close = True
            #     current_screen = None
            #     return

    def navigate_to_play_screen(self):
        print("Navigate to Play screen")
        return playScreen(self.screen, self.game_state)

    def navigate_to_options_screen(self):
        print("Navigate to Options screen")
        return OptionSelectScreen(self.screen, self.game_state)

    def navigate_to_exit_screen(self):
        return None

    def update_objects(self):
        mouse_pos = pygame.mouse.get_pos()
        self.play_button.changeColor(mouse_pos)
        self.options_button.changeColor(mouse_pos)
        self.exit_button.changeColor(mouse_pos)

    def draw_objects(self):
        self.screen.fill((212, 212, 212))
        self.screen.blit(self.background_surf, (0, 0))
        self.title.draw(self.screen)

        self.play_button.update(self.screen)
        self.options_button.update(self.screen)
        self.exit_button.update(self.screen)


class playScreen(screenBase):
    def __init__(self, screen, game_state):
        super().__init__(screen)
        self.game_state = game_state
        self.is_paused = False
        center_x, center_y = 640, 360

        self.background_surf = pygame.image.load("ui/images/Vector.png").convert_alpha()

        orangeButton_surf = pygame.image.load("ui/buttonImages/orangeButton.png").convert_alpha()
        orangeButton_surf = pygame.transform.scale(orangeButton_surf, (100, 30))

        button_font = pygame.font.Font("ui/Font/Minecraftia-Regular.ttf", 13)
        self.button_font = button_font
        self.smallButton_surf = pygame.transform.scale(orangeButton_surf, (30, 30))

        self.turn_context = TurnContext()
        self.create_players() 
        self.deal_hands()
        self.choose_start_player()

        self.draw_sub_buttons = []
        self.available_cards = []
        self.is_stealing = False

        self.draw_button = Button(orangeButton_surf, 475, 340, "Draw", button_font, self.show_draw_options)
        self.steal_button = Button(orangeButton_surf, 585, 340, "Steal", button_font, self.activate_stealing)
        self.trade_button = Button(orangeButton_surf, 695, 340, "Trade", button_font, None)
        self.discard_button = Button(orangeButton_surf, 805, 340, "Discard", button_font, self.handle_discard)
        self.end_turn = Button(orangeButton_surf, 915, 340, "End Turn", button_font, self.trigger_end_turn)

        self.playForMe_button = Button(orangeButton_surf, 980, 40, "Play for me", button_font, None)
        self.guide_button = Button(orangeButton_surf, 1090, 40, "Guide", button_font, None)
        self.pause_button = Button(orangeButton_surf, 1200, 40, "Pause", button_font, None)

        self.resume_button = Button(orangeButton_surf, center_x, center_y - 80, "Resume", button_font, None)
        self.restart_button = Button(orangeButton_surf, center_x, center_y, "Restart", button_font, None)
        self.backMenu_button = Button(orangeButton_surf, center_x, center_y + 80, "Menu", button_font, None)
        self.overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 200))

    def handle_discard(self):
        handle_action_discard_group(self.game_state.current_player, self.game_state.deck, self.turn_context)

    def activate_stealing(self):
        if self.turn_context.has_stolen_card:
            return
        self.is_stealing = True

    def trigger_end_turn(self):
        self.turn_context.reset()
        self.game_state.players.append(self.game_state.current_player)
        self.game_state.current_player = self.game_state.players.popleft()

    def show_draw_options(self):
        if self.turn_context.has_drawn_cards:
            return
        if self.draw_sub_buttons:
            self.draw_sub_buttons = []
            return
        handle_action_draw_3(self.game_state, None, self.turn_context, self.spawn_choice_buttons)

    def spawn_choice_buttons(self, max_draw):
        spacing = 35
        base_x = 440
        base_y = 340 - spacing # Place above the draw button
        for i in range(1, max_draw + 1):
            x_pos = base_x + (i - 1) * spacing
            callback_action = lambda n=i: self.execute_draw(n)
            btn = Button(self.smallButton_surf, x_pos, base_y, str(i), self.button_font, on_click=callback_action)
            self.draw_sub_buttons.append(btn)

    def execute_draw(self, number_of_cards):
        cards = self.game_state.deck.draw_cards(number_of_cards=number_of_cards)
        self.game_state.current_player.draw(cards)
        self.draw_sub_buttons = []
        self.turn_context.has_drawn_cards = True

    def create_players(self):
        players = deque()
        for i in range(self.game_state.number_players):
            players.append(Player(image=None, x=0, y=0, player_id=uuid.uuid4(), hand=[], player_type=PlayerType.HUMAN, name=f"Player {i}"))
        self.game_state.players = players

    def deal_hands(self):
        for player in self.game_state.players:
            player.draw(self.game_state.deck.draw_cards(4))
    
    def choose_start_player(self):
        self.game_state.current_player = self.game_state.players.popleft()

    def process_event(self, event):
        global current_screen

        # Stealing
        # TODO(Nellia): use logic from utils.py, it's not a good place to have this logic here.
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_stealing:
            mouse_x, mouse_y = event.pos
            for card_vis, player, card in self.available_cards:
                if card_vis.contains_point(mouse_x, mouse_y):
                    stolen_card = player.lose_card(player.hand.index(card))
                    self.game_state.current_player.take_card(stolen_card)
                    self.game_state.chosen_player = None
                    self.turn_context.has_stolen_card = True
                    self.is_stealing = False
                    return

        if event.type == pygame.MOUSEBUTTONDOWN:            
            active_buttons = []
            
            if self.is_paused:
                active_buttons = [self.resume_button, self.restart_button, self.backMenu_button]
            else:
                active_buttons = self.draw_sub_buttons + [
                    self.end_turn, 
                    self.discard_button, self.playForMe_button, 
                    self.guide_button, self.pause_button
                ]
                if not self.turn_context.has_drawn_cards:
                    active_buttons += [self.draw_button]
                if not self.turn_context.has_stolen_card:
                    active_buttons += [self.steal_button]
                if not self.turn_context.has_swapped_card:
                    active_buttons += [self.trade_button]

            for button in active_buttons:
                if button.rect.collidepoint(event.pos):
                    screen = button.handle_event(event) 
                    
                    if screen is not None:
                        current_screen = screen
                        self.close = True
                        return

                    return

    def update_objects(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.is_paused:
            # Only update pause menu buttons when paused
            self.resume_button.changeColor(mouse_pos)
            self.restart_button.changeColor(mouse_pos)
            self.backMenu_button.changeColor(mouse_pos)
        else:
            if not self.turn_context.has_drawn_cards:
                self.draw_button.changeColor(mouse_pos)
            if not self.turn_context.has_stolen_card:
                self.steal_button.changeColor(mouse_pos)
            if not self.turn_context.has_swapped_card:
                self.trade_button.changeColor(mouse_pos)
            self.discard_button.changeColor(mouse_pos)
            self.playForMe_button.changeColor(mouse_pos)
            self.guide_button.changeColor(mouse_pos)
            self.pause_button.changeColor(mouse_pos)
            self.end_turn.changeColor(mouse_pos)
            for btn in self.draw_sub_buttons:
                btn.changeColor(mouse_pos)
        # self.player3_button.changeColor(mouse_pos)

    def draw_objects(self):
        self.screen.fill((212, 212, 212))
        self.screen.blit(self.background_surf, (0, 0))
        # self.select_frame.draw(self.screen)
        # self.title_options.draw(self.screen)
        # self.title_players.draw(self.screen)
        # self.title_level.draw(self.screen)
        sprites = CardSprites("cards")
        hand_positions = [
            PlayerHand(700, 70, -40, "horizontal"),
            PlayerHand(852, 600, -40, "horizontal"),
            PlayerHand(426, 600, -40, "horizontal"),
        ]
        i = 0
        self.available_cards = []
        all_players = [self.game_state.current_player] + [p for p in self.game_state.players]
        for player in all_players:
            for card in player.hand:
                color = ""
                if card.color == CardColor.RED:
                    color = "red"
                if card.color == CardColor.BLACK:
                    color = "black"
                if card.color == CardColor.BLUE:
                    color = "blue"
                if card.color == CardColor.YELLOW:
                    color = "yellow"
                if card.color == CardColor.GREEN:
                    color = "green"
                card_vis = CardVisual(color, card.number, sprites)
                if self.is_stealing and player.player_id != self.game_state.current_player.player_id:
                    card_vis.hovered = True
                    self.available_cards.append((card_vis, player, card))
                hand = hand_positions[i]
                hand.add_card(card_vis)
            i += 1
            hand.draw(self.screen)
        if self.is_stealing:
            text = self.button_font.render("SELECT A CARD TO STEAL", True, (255, 0, 0))
            self.screen.blit(text, (600, 300))

        if not self.turn_context.has_drawn_cards:
            self.draw_button.update(self.screen)
        if not self.turn_context.has_stolen_card:
            self.steal_button.update(self.screen)
        if not self.turn_context.has_swapped_card:
            self.trade_button.update(self.screen)
        self.draw_button.update(self.screen)
        self.steal_button.update(self.screen)
        self.trade_button.update(self.screen)
        self.discard_button.update(self.screen)
        self.playForMe_button.update(self.screen)
        self.guide_button.update(self.screen)
        self.pause_button.update(self.screen)
        self.end_turn.update(self.screen)
        for btn in self.draw_sub_buttons:
            btn.update(self.screen)
        # self.player3_button.update(self.screen)
        if self.is_paused:
            self.screen.blit(self.overlay, (0, 0))
            self.resume_button.update(self.screen)
            self.restart_button.update(self.screen)
            self.backMenu_button.update(self.screen)


class OptionSelectScreen(screenBase):
    def __init__(self, screen, game_state: GameState):
        super().__init__(screen)
        self.game_state = game_state

        self.background_surf = pygame.image.load("ui/images/Vector.png").convert_alpha()

        self.select_frame = imageObject("ui/images/selectFrame.png", 640, 365, 'center')

        self.title_options = textObject(520, 135, "Options", "ui/Font/Minecraftia-Regular.ttf", 35, 'Black', 'center')
        self.title_level = textObject(480, 200, "Choose level", "ui/Font/Minecraftia-Regular.ttf", 35, 'Black',
                                      'topleft')
        self.title_players = textObject(480, 390, "Players", "ui/Font/Minecraftia-Regular.ttf", 35, 'Black', 'topleft')

        greenButton_surf = pygame.image.load("ui/buttonImages/greenButton.png").convert_alpha()
        blueButton_surf = pygame.image.load("ui/buttonImages/blueButton.png").convert_alpha()
        redButton_surf = pygame.image.load("ui/buttonImages/redButton.png").convert_alpha()
        yellowButton_surf = pygame.image.load("ui/buttonImages/yellowButton.png").convert_alpha()
        orangeButton_surf = pygame.image.load("ui/buttonImages/orangeButton.png").convert_alpha()
        orangeButton_surf = pygame.transform.scale(orangeButton_surf, (100, 30))

        button_font = pygame.font.Font("ui/Font/Minecraftia-Regular.ttf", 13)
        self.confirm_button = Button(orangeButton_surf, 660, 140, "Confirm", button_font, on_click=self.navigate_to_menu_screen)
        self.back_button = Button(orangeButton_surf, 770, 140, "Back", button_font, on_click=self.navigate_to_menu_screen)
        self.easy_button = Button(greenButton_surf, 520, 310, "Easy", button_font, on_click=self.set_difficult_easy)
        self.medium_button = Button(blueButton_surf, 630, 310, "Medium", button_font, on_click=self.set_difficult_medium)
        self.difficult_button = Button(redButton_surf, 740, 310, "Difficult", button_font, on_click=self.set_difficult_hard)

        self.player1_button = Button(yellowButton_surf, 520, 500, "1 player", button_font, on_click=self.set_1_players)
        self.player2_button = Button(yellowButton_surf, 630, 500, "2 players", button_font, on_click=self.set_2_players)
        self.player3_button = Button(yellowButton_surf, 740, 500, "3 players", button_font, on_click=self.set_3_players)

    def navigate_to_menu_screen(self):
        return menuScreen(self.screen, self.game_state)


    def set_difficult_easy(self):
        self.game_state.set_player_difficulty(PlayerType.COMPUTER_EASY)

    def set_difficult_medium(self):
        self.game_state.set_player_difficulty(PlayerType.COMPUTER_MEDIUM)

    def set_difficult_hard(self):
        self.game_state.set_player_difficulty(PlayerType.COMPUTER_HARD)

    def set_1_players(self):
        self.game_state.set_players(1)

    def set_2_players(self):
        self.game_state.set_players(2)

    def set_3_players(self):
        self.game_state.set_players(3)

    def process_event(self, event):
        global current_screen
        if event.type == pygame.MOUSEBUTTONDOWN:
        #     click_pos = event.pos
            for button in [self.confirm_button, self.back_button, self.easy_button, self.medium_button, self.difficult_button, self.player1_button, self.player2_button, self.player3_button]:
                if button.rect.collidepoint(event.pos):
                    screen = button.handle_event(event)
                    if screen is not None:
                        current_screen = screen
                        print(f"current screen:  {current_screen}")
                        self.close = True
                        return


    def update_objects(self):
        mouse_pos = pygame.mouse.get_pos()
        self.confirm_button.changeColor(mouse_pos)
        self.back_button.changeColor(mouse_pos)
        self.easy_button.changeColor(mouse_pos)
        self.medium_button.changeColor(mouse_pos)
        self.difficult_button.changeColor(mouse_pos)
        self.player1_button.changeColor(mouse_pos)
        self.player2_button.changeColor(mouse_pos)
        self.player3_button.changeColor(mouse_pos)


    def draw_objects(self):
        self.screen.fill((212, 212, 212))
        self.screen.blit(self.background_surf, (0, 0))
        self.select_frame.draw(self.screen)
        self.title_options.draw(self.screen)
        self.title_players.draw(self.screen)
        self.title_level.draw(self.screen)

        self.confirm_button.update(self.screen)
        self.back_button.update(self.screen)

        self.easy_button.update(self.screen)
        self.medium_button.update(self.screen)
        self.difficult_button.update(self.screen)

        self.player1_button.update(self.screen)
        self.player2_button.update(self.screen)
        self.player3_button.update(self.screen)
