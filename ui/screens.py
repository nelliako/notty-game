import pygame
import sys
import uuid
from collections import deque

from Logic.computerLogic.playerDecision import EASY
from ui.button import Button
from ui.objects import imageObject
from ui.text_object import textObject
from Logic.Classes import PlayerType, Player, Deck, GameState, CardColor, PlayerMove, State
from ui.card_sprites import CardSprites
from ui.card_visual import CardVisual
from ui.player_hand import PlayerHand
from ui.deck_ui import Deck as UIDeck
from Logic.utils import TurnContext, handle_action_draw_3, handle_action_steal, handle_action_swap, \
    handle_action_discard_group, get_permissible_moves, get_computer_player_decision, all_hands_non_empty
import random

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
        self.close = True
        print("QUIT EVENT")

        pygame.quit()
        sys.exit()

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

        self.guide_text = self.load_guide_text()
        self.guide_scroll = 0
        self.showing_guide = False

        self.background_surf = pygame.image.load("ui/images/Vector.png").convert_alpha()
        self.playerMe_surf = pygame.image.load("ui/images/playerMe.png").convert_alpha()
        self.player2_surf = pygame.image.load("ui/images/player2.png").convert_alpha()
        # Showing 3rd avatar only if there are 3 players
        if self.game_state.number_players == 3:
            self.player3_surf = pygame.image.load("ui/images/player3.png").convert_alpha()
        self.stateArrow_surf = pygame.image.load("ui/images/arrow.png").convert_alpha()

        deck_surf = pygame.image.load("ui/images/deck.png").convert_alpha()
        card_back_surf = pygame.image.load("ui/images/cardBack.png").convert_alpha()
        deck_center_x = int(1280 * 0.80)
        deck_center_y = 380
        self.deck = UIDeck(deck_surf, deck_center_x, deck_center_y, card_back_surf)

        orangeButton_surf = pygame.image.load("ui/buttonImages/orangeButton.png").convert_alpha()
        orangeButton_surf = pygame.transform.scale(orangeButton_surf, (100, 50))
        roundOrange_surf = pygame.image.load("ui/buttonImages/roundOrange.png").convert_alpha()
        actionButton_surf = pygame.image.load("ui/buttonImages/duckyellowbutton.png").convert_alpha()
        actionButton_surf = pygame.transform.scale(actionButton_surf, (100, 50))
        blue_surf = pygame.image.load("ui/buttonImages/bluebutton.png").convert_alpha()
        blue_surf = pygame.transform.scale(blue_surf, (100, 50))
        playForMe_surf = pygame.image.load("ui/buttonImages/playForMebutton.png").convert_alpha()
        playForMe_surf = pygame.transform.scale(playForMe_surf, (135, 40))
        pause_surf = pygame.image.load("ui/buttonImages/pause.png").convert_alpha()
        pause_surf = pygame.transform.scale(pause_surf, (40, 40))
        guide_surf = pygame.transform.scale(blue_surf, (80, 40))

        button_font = pygame.font.Font("ui/Font/Minecraftia-Regular.ttf", 13)
        self.button_font = button_font
        self.smallButton_surf = pygame.transform.scale(roundOrange_surf, (30, 30))

        # Preparing the "start state"
        self.create_players() 
        self.deal_hands()
        self.choose_start_player()
        self.reset_state()

        # FIXED UI POSITIONS FOR UP TO 3 PLAYERS
        self.hand_bottom = PlayerHand(640, 520, -18, "horizontal")   # Player 0 - Bottom
        self.hand_top    = PlayerHand(640, 100, -18, "horizontal")    # Player 1 - Top
        self.hand_left   = PlayerHand(100, 360, -18, "vertical")     # Player 2 - Left
        self.ui_hands = []
        self.ui_hands.append(self.hand_bottom)
        if self.game_state.number_players >= 2:
            self.ui_hands.append(self.hand_top)
        if self.game_state.number_players == 3:
            self.ui_hands.append(self.hand_left)


        self.draw_button = Button(actionButton_surf, 460, 340, "Draw", button_font, self.show_draw_options)
        self.steal_button = Button(actionButton_surf, 580, 340, "Steal", button_font, self.activate_stealing)
        self.trade_button = Button(actionButton_surf, 700, 340, "Trade", button_font, self.activate_trading)
        self.discard_button = Button(actionButton_surf, 820, 340, "Discard", button_font, self.handle_discard)
        self.end_turn = Button(blue_surf, 1210, 670, "End Turn", button_font, self.trigger_end_turn)

        self.guide_button = Button(guide_surf, 1025, 40, "Guide", button_font, self.open_guide)
        self.playForMe_button = Button(playForMe_surf, 1145, 40, "", button_font, self.play_for_me_button)
        self.pause_button = Button(pause_surf, 1245, 40, "", button_font, self.pause_game)

        self.resume_button = Button(orangeButton_surf, center_x, center_y - 80, "Resume", button_font, self.resume_game)
        self.restart_button = Button(orangeButton_surf, center_x, center_y, "Restart", button_font, self.restart_game)
        self.backMenu_button = Button(orangeButton_surf, center_x, center_y + 80, "Menu", button_font, self.navigate_to_menu_screen)
        self.overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 200))
        # Selection persistence and draw-order tracking
        self.card_states = {} # card_id -> selected(bool)
        self.last_hand_visuals = [] # list of (card_vis, logic_card, player)

    def pause_game(self):
        self.is_paused = True

    def resume_game(self):
        self.is_paused = False

    def reset_state(self):
        self.permissible_moves = []
        self.done_moves = []
        self.draw_sub_buttons = []
        self.available_cards_for_steal_or_trade = []
        self.is_stealing = False
        self.is_trading = False

    def restart_game(self):
        self.game_state.reset_state()
        self.create_players()
        self.deal_hands()
        self.choose_start_player()
        self.is_paused = False
        self.reset_state()

    def navigate_to_menu_screen(self):
        self.game_state.reset_state()
        return menuScreen(self.screen, self.game_state), None

    def play_for_me_button(self):
        self.game_state.computer_playing_for_human = True
        return None, EASY(self.game_state, self.permissible_moves)

    #/guide
    def load_guide_text(self):
        with open("ui/guide_text/nottyGuide.txt", "r", encoding="utf-8") as f:
            return f.read().splitlines()

    def open_guide(self):
        self.showing_guide = True
        self.guide_scroll = 0

    def close_guide(self):
        self.showing_guide = False

    def draw_guide(self):
        self.screen.blit(self.overlay, (0, 0))
        screen_center_x = 640
        screen_center_y = 360
        target_width = 600
        target_height = 600
        panel_x = screen_center_x - (target_width // 2)
        panel_y = screen_center_y - (target_height // 2)

        paper_object = imageObject("ui/images/guidePaper.png", screen_center_x, screen_center_y, 'center')
        paper_object.scale(target_width, target_height)
        paper_object.rect.topleft = (panel_x, panel_y)
        paper_object.draw(self.screen)

        font = pygame.font.Font("ui/Font/Minecraftia-Regular.ttf", 20)
        text_line_height = font.get_linesize()
        text_x = panel_x + 90  # 从70改成90，再增加左边距
        text_y = panel_y + 30 + self.guide_scroll

        start_y = panel_y + 30
        max_draw_y = panel_y + target_height - 30

        max_text_width = target_width - 180  # 从140改成180，左右各90px边距，所以减180

        all_lines = []
        for line in self.guide_text:
            if line == "":
                all_lines.append("")
            else:
                text_surf = font.render(line, True, (0, 0, 0))
                if text_surf.get_width() <= max_text_width:
                    all_lines.append(line)
                else:
                    words = line.split(" ")
                    current_line = ""
                    for word in words:
                        test_line = current_line + " " + word if current_line else word
                        test_surf = font.render(test_line, True, (0, 0, 0))
                        if test_surf.get_width() <= max_text_width:
                            current_line = test_line
                        else:
                            if current_line:
                                all_lines.append(current_line)
                            current_line = word
                    if current_line:
                        all_lines.append(current_line)

        total_content_height = len(all_lines) * text_line_height
        viewport_height = target_height - 60
        self.max_scroll = max(0, total_content_height - viewport_height)

        if self.guide_scroll > 0:
            self.guide_scroll = 0
        if self.guide_scroll < -self.max_scroll:
            self.guide_scroll = -self.max_scroll

        text_y = panel_y + 30 + self.guide_scroll

        for line in all_lines:
            if text_y + text_line_height > max_draw_y:
                break
            elif text_y >= start_y:
                surf = font.render(line, True, (0, 0, 0))
                self.screen.blit(surf, (text_x, text_y))
            text_y += text_line_height

        close_x = panel_x + target_width - 25
        close_y = panel_y + 25

        close_surf = pygame.image.load("ui/buttonImages/closeButton.png").convert_alpha()
        close_surf = pygame.transform.scale(close_surf, (40, 40))

        self.closeGuide_button = Button(close_surf, close_x, close_y, "", self.button_font, self.close_guide)

        self.closeGuide_button.update(self.screen)
    #/guide

    def handle_discard(self):
        if self.is_trading:
            return
        handle_action_discard_group(self.game_state, None)

    def activate_trading(self):
        if self.is_stealing:
            self.is_trading = False
            return
        self.is_trading = True
        cards_from_the_deck = self.game_state.deck.draw_cards(1)
        self.game_state.current_player.draw(cards_from_the_deck)

    def activate_stealing(self):
        if self.is_trading:
            self.is_stealing = False
            return
 
        # Exiting the stealing mode if it was pressed again, the implication in the draw function: getting rid of the text in draw objects if the steal mode has been activated 
        if self.is_stealing:
            self.is_stealing = False
            return
        self.is_stealing = True
    
    def trigger_end_turn(self):
        self.reset_state()
        self.game_state.players.append(self.game_state.current_player)
        self.game_state.current_player = self.game_state.players.popleft()

    def show_draw_options(self):
        if self.is_trading:
            return
        if self.draw_sub_buttons:
            self.draw_sub_buttons = []
            return
        handle_action_draw_3(self.game_state, None, None, self.create_choice_buttons)

    def create_choice_buttons(self, max_draw):
        spacing = 35
        base_x = 425
        base_y = 325 - spacing # Place above the draw button
        for i in range(1, max_draw + 1):
            x_pos = base_x + (i - 1) * spacing
            callback_action = lambda n=i: self.execute_draw(n)
            btn = Button(self.smallButton_surf, x_pos, base_y, str(i), self.button_font, on_click=callback_action)
            self.draw_sub_buttons.append(btn)

    def execute_draw(self, number_of_cards): #added this to check functionality of animation
        cards = self.game_state.deck.draw_cards(number_of_cards=number_of_cards)
        self.game_state.current_player.draw(cards)
        self.draw_sub_buttons = []
        self.done_moves.append(PlayerMove.DRAW)

        dest_x, dest_y = 640, 500
        for i in range(number_of_cards):
            self.deck.start_draw_animation(dest_x + i * 20, dest_y, speed=12.0)

    def create_players(self):
        self.game_state.players.clear()
        # players = deque()
        for i in range(self.game_state.number_players):
            if i == 0:
                self.game_state.players.append(Player(image=None, x=0, y=0, player_id=uuid.uuid4(), hand=[], player_type=PlayerType.HUMAN, name=f"Player {i}"))
            else:
                self.game_state.players.append(Player(image=None, x=0, y=0, player_id=uuid.uuid4(), hand=[], player_type=self.game_state.computer_difficulty, name=f"Player {i}"))
        # self.game_state.players = players

    def deal_hands(self):
        for player in self.game_state.players:
            player.draw(self.game_state.deck.draw_cards(4))
    
    def choose_start_player(self):
        self.game_state.current_player = self.game_state.players.popleft()

    def process_event(self, event):
        global current_screen

        if self.showing_guide:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.guide_scroll += 24
                elif event.button == 5:
                    self.guide_scroll -= 24

                if self.guide_scroll > 0:
                    self.guide_scroll = 0

                if hasattr(self, 'max_scroll'):
                    if self.guide_scroll < -self.max_scroll:
                        self.guide_scroll = -self.max_scroll

                if hasattr(self, "closeGuide_button"):
                    if self.closeGuide_button.rect.collidepoint(event.pos):
                        self.close_guide()
            return

        # print(f"Game State Deck size: {len(self.game_state.deck.cards)}")

        total_cards = list(self.game_state.deck.cards)
        for player in [self.game_state.current_player] + list(self.game_state.players):
            if player is None:
                continue
            # print(f"{player.name}'s hand size: {len(player.hand)}!")
            if player.hand is not None:
                total_cards += list(player.hand)

        # print(f"Total Cards: {len(total_cards)}")

        if len(total_cards) > 90:
            seen_ids = set()
            unique_cards = []

            for card in total_cards:
                if card.id not in seen_ids:
                    unique_cards.append(card)
                    seen_ids.add(card.id)

            print(unique_cards)
            print(seen_ids)
            # Note: avoid hard crash; log warning instead
            print("[Warning] Cards in deck exceeds 90 cards! Continuing without raising.")

        # print(f"Game state Current Player {self.game_state.current_player.name} Hand Size: {len(self.game_state.current_player.hand)}")
        if len(self.game_state.current_player.hand) > 21 or (len(self.game_state.current_player.hand) == 21 and not self.is_trading):
            raise ValueError(f"{self.game_state.current_player.name}'s hand exceeds 20 cards!")


        if self.game_state.current_player.type != PlayerType.HUMAN:
            computer_player_decision = get_computer_player_decision(game_state=self.game_state, moves=self.permissible_moves)
            move, _ = computer_player_decision.choose()
            print(f"{self.game_state.current_player.name} chose move: {move}")

            # Getting rid of the chosen buttons when computer player is playing (if it's not a discard button)
            if move in [PlayerMove.DRAW, PlayerMove.TAKE, PlayerMove.DRAW_ONE]:
                self.done_moves.append(move)

            while True:
                if move == PlayerMove.DRAW:
                    handle_action_draw_3(self.game_state, computer_player_decision)
                    break

                if move == PlayerMove.TAKE:
                    handle_action_steal(self.game_state, computer_player_decision)
                    break

                if move == PlayerMove.DRAW_ONE:
                    handle_action_swap(self.game_state, computer_player_decision)
                    break

                if move == PlayerMove.DISCARD_VALID_CARDS:
                    handle_action_discard_group(self.game_state)
                    break

                if move == PlayerMove.END_TURN or move == PlayerMove.PASS:
                    self.trigger_end_turn()
                    break

        if not all_hands_non_empty(self.game_state):
            # TODO replace with a function & return winning player
            for player in self.game_state.players:
                if len(player.hand) == 0:
                    print(f'The winner is {player.name}')
                    if player.type == PlayerType.HUMAN:
                        self.game_state.state = State.WON
                    else:
                        self.game_state.state = State.LOST
                    is_endgame = True
                    break

            self.game_state.reset_state()
            # TODO replace with Game Over Screen
            current_screen = EndScreen(self.screen, self.game_state)
            print(f"current screen:  {current_screen}")
            self.close = True
            return

        # Stealing
        # TODO(Nellia): use logic from utils.py, it's not a good place to have this logic here.
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_stealing:
            mouse_x, mouse_y = event.pos
            for card_vis, player, card in self.available_cards_for_steal_or_trade:
                if card_vis.contains_point(mouse_x, mouse_y):
                    stolen_card = player.lose_card(random.randint(0, (len(player.hand)-1)))
                    self.game_state.current_player.take_card(stolen_card)
                    self.game_state.chosen_player = None
                    self.is_stealing = False
                    self.done_moves.append(PlayerMove.TAKE)
                    return
                
        # Trading
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_trading:
            mouse_x, mouse_y = event.pos
            for card_vis, player, card in reversed(self.available_cards_for_steal_or_trade): # needs to be changed
                if card_vis.contains_point(mouse_x, mouse_y):
                    handle_action_swap(self.game_state, None, None, lambda: player.hand.index(card), skip_drawing=True)
                    self.is_trading = False
                    self.done_moves.append(PlayerMove.DRAW_ONE)
                    return
        

        if event.type == pygame.MOUSEBUTTONDOWN:            
            active_buttons = []
            
            if self.is_paused:
                active_buttons = [self.resume_button, self.restart_button, self.backMenu_button]
            else:
                active_buttons = self.draw_sub_buttons + [
                    self.end_turn, self.discard_button, self.playForMe_button, self.guide_button, self.pause_button
                ]
                if PlayerMove.DRAW in self.permissible_moves:
                    active_buttons += [self.draw_button]
                if PlayerMove.TAKE in self.permissible_moves:
                    active_buttons += [self.steal_button]
                if PlayerMove.DRAW_ONE in self.permissible_moves:
                    active_buttons += [self.trade_button]

            for button in active_buttons:
                if button.rect.collidepoint(event.pos):
                    try:
                        screen, computer_player_decision = button.handle_event(event)
                        if screen is not None:
                            current_screen = screen
                            self.close = True
                            return
                        if computer_player_decision is not None and self.game_state.computer_playing_for_human:
                            move, _ = computer_player_decision.choose()
                            print(f"On behalf of {self.game_state.current_player.name}, the computer chose move: {move}")

                            # Getting rid of the chosen buttons when computer player is playing (if it's not a discard button)
                            if move in [PlayerMove.DRAW, PlayerMove.TAKE, PlayerMove.DRAW_ONE]:
                                self.done_moves.append(move)

                            while True:
                                if move == PlayerMove.DRAW:
                                    handle_action_draw_3(self.game_state, computer_player_decision)
                                    self.game_state.computer_playing_for_human = False
                                    break

                                if move == PlayerMove.TAKE:
                                    handle_action_steal(self.game_state, computer_player_decision)
                                    self.game_state.computer_playing_for_human = False
                                    break

                                if move == PlayerMove.DRAW_ONE:
                                    handle_action_swap(self.game_state, computer_player_decision)
                                    self.game_state.computer_playing_for_human = False
                                    break

                                if move == PlayerMove.DISCARD_VALID_CARDS:
                                    handle_action_discard_group(self.game_state)
                                    self.game_state.computer_playing_for_human = False
                                    break

                                if move == PlayerMove.END_TURN or move == PlayerMove.PASS:
                                    self.game_state.computer_playing_for_human = False
                                    self.trigger_end_turn()
                                    break
                            return
                    except Exception as e:
                        return
                    return

            # Card click selection with overlap-aware hit regions
            # Overlap-aware card click selection (horizontal/vertical)
            if not self.is_paused and not self.is_stealing and not self.is_trading and self.last_hand_visuals:
                mx, my = event.pos
                # Build per-hand groups to know draw order
                hand_groups = {}
                for card_vis, logic_card, player, hand, card_index in self.last_hand_visuals:
                    hand_groups.setdefault(hand, []).append((card_vis, logic_card, player, hand, card_index))

                for hand, entries in hand_groups.items():
                    # entries are stored in draw order (earlier added drawn earlier)
                    # Iterate from topmost (last) backwards
                    for idx in range(len(entries)-1, -1, -1):
                        card_vis, logic_card, player, h_ref, card_index = entries[idx]
                        hit = False
                        if hand.orientation == "horizontal" and idx < len(entries) - 1:
                            visible_width = abs(hand.spacing)
                            hover_rect = pygame.Rect(card_vis.x + card_vis.width - visible_width, card_vis.base_y, visible_width, card_vis.height)
                            hit = hover_rect.collidepoint(mx, my)
                        elif hand.orientation == "vertical" and idx < len(entries) - 1:
                            # For vertical stacks, only the TOP strip of a covered card remains visible
                            visible_height = abs(hand.spacing)
                            hover_rect = pygame.Rect(card_vis.x, card_vis.base_y, card_vis.width, visible_height)
                            hit = hover_rect.collidepoint(mx, my)
                        else:
                            hit = card_vis.contains_point(mx, my)
                        if hit:
                            current_sel = self.card_states.get(logic_card.id, False)
                            self.card_states[logic_card.id] = not current_sel
                            break  # stop searching this hand
                    # allow selecting one card per hand per click

        if not all_hands_non_empty(self.game_state):
            if not all_hands_non_empty(self.game_state):
                for player in self.game_state.players:
                    if len(player.hand) == 0:
                        print(f'The winner is {player.name}')
                        if player.type == PlayerType.HUMAN:
                            self.game_state.state = State.WON
                        else:
                            self.game_state.state = State.LOST
                        # is_endgame = True
                        break

            self.game_state.reset_state()
            current_screen = EndScreen(self.screen, self.game_state)
            print(f"current screen:  {current_screen}")
            self.close = True
            return

    def update_objects(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.is_paused:
            # Only update pause menu buttons when paused
            self.resume_button.changeColor(mouse_pos)
            self.restart_button.changeColor(mouse_pos)
            self.backMenu_button.changeColor(mouse_pos)
        else:
            if PlayerMove.DRAW in self.permissible_moves:
                self.draw_button.changeColor(mouse_pos)
            if PlayerMove.TAKE in self.permissible_moves:
                self.steal_button.changeColor(mouse_pos)
            if PlayerMove.DRAW_ONE in self.permissible_moves:
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
        self.screen.blit(self.stateArrow_surf, (650, 585))
        self.screen.blit(self.playerMe_surf, (640, 610))
        self.screen.blit(self.player2_surf, (640, 90))
        # Showing 3rd avatar only if there are 3 players
        if self.game_state.number_players == 3:
            self.screen.blit(self.player3_surf, (80, 305))

        self.deck.draw_deck(self.screen)
        self.deck.update_and_draw_animations(self.screen)

        # Calculating all available moves
        self.permissible_moves = get_permissible_moves(self.game_state)
        for move in self.done_moves:
            if move in self.permissible_moves:
                self.permissible_moves.remove(move)
        sprites = CardSprites("cardsImages")
        for hand in self.ui_hands:
            hand.cards = []

        hand_bottom = PlayerHand(640, 450, -18, "horizontal")
        hand_top    = PlayerHand(640, 160, -18, "horizontal")
        hand_left   = PlayerHand(200, 320, -18, "vertical")
        hand_positions = [hand_bottom, hand_top, hand_left]
        self.available_cards_for_steal_or_trade = []
        # Drawing all cards of all players
        mx, my = pygame.mouse.get_pos()

        all_players = [self.game_state.current_player] + list(self.game_state.players)
        self.last_hand_visuals = []
        for i, player in enumerate(all_players):
                if i >= len(self.ui_hands):
                    break

                hand = self.ui_hands[i]
                hand.cards = []
                for card_index, card in enumerate(player.hand):
                    card_vis = CardVisual(card.color.display_name, card.number, sprites)
                    # If we are in a "steal" mode we need to remember cards we can steal and show them as "hovered"
                    if self.is_stealing and player.player_id != self.game_state.current_player.player_id:
                        card_vis.hovered = True
                        self.available_cards_for_steal_or_trade.append((card_vis, player, card))

                    # If we are in the trading mode
                    elif self.is_trading and player.player_id == self.game_state.current_player.player_id:
                        card_vis.hovered = True
                        self.available_cards_for_steal_or_trade.append((card_vis, player, card))
                    # Apply persistent selected state
                    selected_state = self.card_states.get(card.id, False)
                    card_vis.selected = selected_state
                    # Regular hover (only when not in steal mode)
                    if not self.is_stealing:
                        if card_vis.contains_point(mx, my):
                            card_vis.hovered = True
                    hand = self.ui_hands[i]
                    hand.add_card(card_vis)
                    self.last_hand_visuals.append((card_vis, card, player, hand, card_index))
                # Defer drawing until after overlap-aware hover is computed
                mx, my = pygame.mouse.get_pos()

        # Overlap-aware hover regions (no redraw to avoid bringing to top)
        if not self.is_stealing and self.last_hand_visuals:
            mx, my = pygame.mouse.get_pos()
            hand_groups = {}
            for card_vis, logic_card, player, hand, card_index in self.last_hand_visuals:
                hand_groups.setdefault(hand, []).append((card_vis, logic_card, player, hand, card_index))

            for hand, entries in hand_groups.items():
                for idx, (card_vis, logic_card, player, h_ref, card_index) in enumerate(entries):
                    if hand.orientation == "horizontal" and idx < len(entries) - 1:
                        visible_width = abs(hand.spacing)
                        hover_rect = pygame.Rect(card_vis.x + card_vis.width - visible_width, card_vis.base_y, visible_width, card_vis.height)
                        card_vis.hovered = hover_rect.collidepoint(mx, my)
                    elif hand.orientation == "vertical" and idx < len(entries) - 1:
                        # For vertical stacks, only the TOP strip of a covered card remains visible
                        visible_height = abs(hand.spacing)
                        hover_rect = pygame.Rect(card_vis.x, card_vis.base_y, card_vis.width, visible_height)
                        card_vis.hovered = hover_rect.collidepoint(mx, my)
                    else:
                        card_vis.hovered = card_vis.contains_point(mx, my)

        # Draw all hands once with final hover flags so overlays show without lifting
        for hand in self.ui_hands:
            hand.draw(self.screen)

        # Prompting the user to steal if it's stealing (relevant for human player)
        if self.is_stealing:
            text = self.button_font.render("SELECT A PLAYER TO STEAL A RANDOM CARD", True, (255, 0, 0))
            self.screen.blit(text, (475, 290))

        if self.is_trading:
            # There should be a card appearing on the screen drawn from the deck 
            text = self.button_font.render("DISCARD ANY CARD FROM YOUR HAND", True, (255, 0, 0))
            self.screen.blit(text, (475, 290))

        # Drawing buttons for permissible moves
        if PlayerMove.DRAW in self.permissible_moves:
            self.draw_button.update(self.screen)
        if PlayerMove.TAKE in self.permissible_moves:
            self.steal_button.update(self.screen)
        # This is because we need to get rid of the button straight after we entered the mode to avoid cheating
        if PlayerMove.DRAW_ONE in self.permissible_moves and not self.is_trading:
            self.trade_button.update(self.screen)

        self.discard_button.update(self.screen)
        self.playForMe_button.update(self.screen)
        self.pause_button.update(self.screen)
        self.guide_button.update(self.screen)
        self.pause_button.update(self.screen)

        # To prevent cheating and bugs by ending the turn prematurely
        if not self.is_trading:
            self.end_turn.update(self.screen)

        self.end_turn.update(self.screen)
        for btn in self.draw_sub_buttons:
            btn.update(self.screen)
        # self.player3_button.update(self.screen)
        if self.is_paused:
            self.screen.blit(self.overlay, (0, 0))
            self.resume_button.update(self.screen)
            self.restart_button.update(self.screen)
            self.backMenu_button.update(self.screen)

        if self.showing_guide:
            self.draw_guide()
            return


class OptionSelectScreen(screenBase):
    def __init__(self, screen, game_state: GameState):
        super().__init__(screen)
        self.game_state = game_state

        self.background_surf = pygame.image.load("ui/images/Vector.png").convert_alpha()

        self.select_frame = imageObject("ui/images/selectFrame.png", 640, 365, 'center')

        font_path = "ui/Font/Minecraftia-Regular.ttf"
        self.title_options = textObject(520, 135, "Options", font_path, 35, 'Black', 'center')
        self.title_level = textObject(480, 200, "Choose level", font_path, 35, 'Black',
                                      'topleft')
        self.title_players = textObject(480, 390, "Players", font_path, 35, 'Black', 'topleft')

        greenButton_surf = pygame.image.load("ui/buttonImages/greenButton.png").convert_alpha()
        greenButton_surf_selected = pygame.image.load("ui/buttonImages/selectedGreen.png").convert_alpha()
        blueButton_surf = pygame.image.load("ui/buttonImages/blueButton.png").convert_alpha()
        blueButton_surf_selected = pygame.image.load("ui/buttonImages/selectedBlue.png").convert_alpha()
        redButton_surf = pygame.image.load("ui/buttonImages/redButton.png").convert_alpha()
        redButton_surf_selected = pygame.image.load("ui/buttonImages/selectedRed.png").convert_alpha()
        yellowButton_surf = pygame.image.load("ui/buttonImages/yellowButton.png").convert_alpha()
        yellowButton_surf_selected = pygame.image.load("ui/buttonImages/selectedYellow.png").convert_alpha()
        orangeButton_surf = pygame.image.load("ui/buttonImages/orangeButton.png").convert_alpha()
        orangeButton_surf = pygame.transform.scale(orangeButton_surf, (100, 30))

        button_font = pygame.font.Font(font_path, 13)
        self.confirm_button = Button(orangeButton_surf, 660, 140, "Confirm", button_font, on_click=self.navigate_to_menu_screen)
        self.back_button = Button(orangeButton_surf, 770, 140, "Back", button_font, on_click=self.navigate_to_menu_screen)
        self.easy_button = Button(greenButton_surf, 520, 310, "Easy", button_font, on_click=self.set_difficult_easy)
        self.medium_button = Button(blueButton_surf, 630, 310, "Medium", button_font, on_click=self.set_difficult_medium)
        self.difficult_button = Button(redButton_surf, 740, 310, "Difficult", button_font, on_click=self.set_difficult_hard)

        self.player2_button = Button(yellowButton_surf, 520, 500, "2 players", button_font, on_click=self.set_2_players)
        self.player3_button = Button(yellowButton_surf, 650, 500, "3 players", button_font, on_click=self.set_3_players)

        self.easy_button.selected_image = greenButton_surf_selected
        self.medium_button.selected_image = blueButton_surf_selected
        self.difficult_button.selected_image = redButton_surf_selected
        self.player2_button.selected_image = yellowButton_surf_selected
        self.player3_button.selected_image = yellowButton_surf_selected

        self.difficulty_buttons = [self.easy_button, self.medium_button, self.difficult_button]

        self.player_buttons = [self.player2_button, self.player3_button]

    def navigate_to_menu_screen(self):
        return menuScreen(self.screen, self.game_state)

    def select_only(self, selected_button, group):
        for btn in group:
            btn.is_selected = (btn is selected_button)

    def set_difficult_easy(self):
        self.game_state.set_player_difficulty(PlayerType.COMPUTER_EASY)
        self.select_only(self.easy_button, self.difficulty_buttons)

    def set_difficult_medium(self):
        self.game_state.set_player_difficulty(PlayerType.COMPUTER_MEDIUM)
        self.select_only(self.medium_button, self.difficulty_buttons)

    def set_difficult_hard(self):
        self.game_state.set_player_difficulty(PlayerType.COMPUTER_HARD)
        self.select_only(self.difficult_button, self.difficulty_buttons)

    def set_2_players(self):
        self.game_state.set_players(2)
        self.select_only(self.player2_button, self.player_buttons)

    def set_3_players(self):
        self.game_state.set_players(3)
        self.select_only(self.player3_button, self.player_buttons)

    def process_event(self, event):
        global current_screen
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Iterate only over defined buttons
            for button in [self.confirm_button, self.back_button, self.easy_button, self.medium_button, self.difficult_button, self.player2_button, self.player3_button]:
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

        self.player2_button.update(self.screen)
        self.player3_button.update(self.screen)

class EndScreen(screenBase):
    def __init__(self, screen, game_state: GameState):
        super().__init__(screen)
        self.game_state = game_state
        font_path = "ui/Font/Minecraftia-Regular.ttf"
        self.WinResult = textObject(640, 220, "YOU WIN!", font_path, 150, 'Black', 'center')
        self.LoseResult = textObject(640, 220, "YOU LOSE!", font_path, 150, 'Black', 'center')

        self.win_colors = [(255,65,65),(87,255,115),(171, 87, 255),(87,245,255)]
        self.win_color_index = 0
        self.win_animation_font = pygame.font.Font("ui/Font/Minecraftia-Regular.ttf", 150)

        self.background_surf = pygame.image.load("ui/images/Vector.png").convert_alpha()

        button_surf = pygame.image.load("ui/buttonImages/duckyellowbutton.png").convert_alpha()
        button_surf = pygame.transform.scale(button_surf, (200, 50))

        center_x, center_y = 640, 360
        button_font = pygame.font.Font(font_path, 20)
        self.restart_button = Button(button_surf, center_x-150, center_y + 150, "Restart", button_font, self.navigate_to_restart)
        self.backMenu_button = Button(button_surf, center_x+150, center_y +150, "Menu", button_font, self.navigate_to_menu)

        self.win_flash_timer = pygame.USEREVENT + 10
        pygame.time.set_timer(self.win_flash_timer, 200)

    def navigate_to_restart(self):
        self.game_state.reset_state()
        return playScreen(self.screen, self.game_state)

    def navigate_to_menu(self):
        return menuScreen(self.screen, self.game_state)

    def update_objects(self):
        mouse_pos = pygame.mouse.get_pos()
        self.restart_button.changeColor(mouse_pos)
        self.backMenu_button.changeColor(mouse_pos)

    def process_event(self, event):
        global current_screen

        if event.type == self.win_flash_timer:
            self.win_color_index = (self.win_color_index + 1) % len(self.win_colors)
            self.WinResult.color = self.win_colors[self.win_color_index]
            self.WinResult.render()

        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in [self.restart_button, self.backMenu_button]:
                screen = button.handle_event(event)
                if screen is not None:
                    current_screen = screen
                    self.close = True
                    return

    def draw_objects(self):
        self.screen.fill((212, 212, 212))
        self.screen.blit(self.background_surf, (0, 0))

        self.restart_button.update(self.screen)
        self.backMenu_button.update(self.screen)

        # print(f"Game state state: {self.game_state.state}")
        if self.game_state.state == State.WON:
            self.WinResult.draw(self.screen)
        elif self.game_state.state == State.LOST:
            self.LoseResult.draw(self.screen)
