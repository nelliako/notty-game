import pygame
import sys
import uuid
import time
from collections import deque
import gif_pygame

from Logic.computerLogic.playerDecision import *
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
from ui.sounds import GameSound

current_screen = None
game_sound = None

class screenBase():
    def __init__(self, screen):
        global game_sound
        self.screen = screen
        self.close = False
        if game_sound is None:
            game_sound = GameSound()
        self.sound = game_sound

    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.sound.playClick()
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
        soundOn_surf = pygame.image.load("ui/buttonImages/speaker.png").convert_alpha()
        soundOn_surf = pygame.transform.scale(soundOn_surf, (30, 30))
        soundOff_surf = pygame.image.load("ui/buttonImages/mute.png").convert_alpha()
        soundOff_surf = pygame.transform.scale(soundOff_surf, (30, 30))

        button_font = pygame.font.Font("ui/Font/Minecraftia-Regular.ttf", 20)
        self.play_button = Button(button_surf, 640, 450, "Play", button_font, self.navigate_to_play_screen)
        self.options_button = Button(button_surf, 640, 530, "Options", button_font, self.navigate_to_options_screen)
        self.exit_button = Button(button_surf, 640, 610, "Exit", button_font, self.navigate_to_exit_screen)
        self.speaker_button = Button(soundOn_surf, 40, 40, "", button_font, self.toggle_sound)
        self.mute_button = Button(soundOff_surf, 40, 40, "", button_font, self.toggle_sound)
        self.is_muted = False

    def toggle_sound(self):
        if self.is_muted:
            self.is_muted = False
            self.sound.unpauseBackgroundMusic()
        else:
            self.is_muted = True
            self.sound.pauseBackgroundMusic()

    def process_event(self, event):
        global current_screen
        super().process_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.is_muted:
                if self.speaker_button.rect.collidepoint(event.pos):
                    self.toggle_sound()
                    return
            else:
                if self.mute_button.rect.collidepoint(event.pos):
                    self.toggle_sound()
                    return
            
            for button in [self.play_button, self.options_button, self.exit_button]:
                if button.rect.collidepoint(event.pos):
                    screen = button.handle_event(event)
                    if screen is not None:
                        current_screen = screen
                        print(f"current screen:  {current_screen}")
                        self.close = True
                        return



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
        
        if self.is_muted:
            self.mute_button.update(self.screen)
        else:
            self.speaker_button.update(self.screen)


class playScreen(screenBase):
    def __init__(self, screen, game_state):
        super().__init__(screen)
        self.game_state = game_state
        # Setting the time to ensure the animation for hands dealing in the beginning works
        self.start_time = pygame.time.get_ticks()
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
        self.discard_m_surf = pygame.image.load("ui/images/discard_m.png").convert_alpha()
        self.steal_m_surf = pygame.image.load("ui/images/steal_m.png").convert_alpha()
        
        # Create rectangles for player avatar positions (for stealing clicks)
        self.player2_rect = pygame.Rect(600, 200, self.player2_surf.get_width(), self.player2_surf.get_height())
        if self.game_state.number_players == 3:
            self.player3_rect = pygame.Rect(230, 305, self.player3_surf.get_width(), self.player3_surf.get_height())

        deck_surf = pygame.image.load("ui/images/deck.png").convert_alpha()
        card_back_surf = pygame.image.load("ui/images/cardBack.png").convert_alpha()
        deck_center_x = int(1280 * 0.80)
        deck_center_y = 380
        self.deck = UIDeck(deck_surf, deck_center_x, deck_center_y, card_back_surf)
      
        self.shuffle_gif = gif_pygame.load("ui/images/shuffle.gif")
        
        # Shuffle animation state
        self.showing_shuffle_animation = False
        self.shuffle_animation_start_time = 0

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
        soundOn_surf = pygame.image.load("ui/buttonImages/speaker.png").convert_alpha()
        soundOn_surf = pygame.transform.scale(soundOn_surf, (30, 30))
        soundOff_surf = pygame.image.load("ui/buttonImages/mute.png").convert_alpha()
        soundOff_surf = pygame.transform.scale(soundOff_surf, (30, 30))

        button_font = pygame.font.Font("ui/Font/Minecraftia-Regular.ttf", 13)
        self.button_font = button_font
        self.smallButton_surf = pygame.transform.scale(roundOrange_surf, (30, 30))

        # FIXED UI POSITIONS FOR UP TO 3 PLAYERS
        self.hand_bottom = PlayerHand(600, 580, -18, "horizontal")   # Player 0 - Bottom
        self.hand_top    = PlayerHand(600, 50, -18, "horizontal")    # Player 1 - Top
        self.hand_left   = PlayerHand(100, 300, -18, "vertical")     # Player 2 - Left
        self.ui_hands = []
        self.ui_hands.append(self.hand_bottom)
        if self.game_state.number_players >= 2:
            self.ui_hands.append(self.hand_top)
        if self.game_state.number_players == 3:
            self.ui_hands.append(self.hand_left)

        # Preparing the "start state"
        self.create_players() 
        self.deal_hands()
        self.choose_start_player()
        self.reset_state()


        self.draw_button = Button(actionButton_surf, 460, 350, "Draw", button_font, self.show_draw_options)
        self.steal_button = Button(actionButton_surf, 580, 350, "Steal", button_font, self.activate_stealing)
        self.trade_button = Button(actionButton_surf, 700, 350, "Trade", button_font, self.activate_trading)
        self.discard_button = Button(actionButton_surf, 820, 350, "Discard", button_font, self.handle_discard)
        self.end_turn = Button(blue_surf, 1210, 670, "End Turn", button_font, self.trigger_end_turn)

        self.speaker_button = Button(soundOn_surf, 40, 40, "", button_font, self.toggle_sound)
        self.mute_button = Button(soundOff_surf, 40, 40, "", button_font, self.toggle_sound)
        self.is_muted = False

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
        self.selected_player_for_steal = None
        self.shuffle_sound_played = False  # Flag to play shuffle sound only once

    def toggle_sound(self):
        if self.is_muted:
            self.is_muted = False
            self.sound.unpauseBackgroundMusic()
        else:
            self.is_muted = True
            self.sound.pauseBackgroundMusic()

    def pause_game(self):
        self.is_paused = True

    def resume_game(self):
        self.is_paused = False

    def reset_state(self):
        self.permissible_moves = [] # get_permissible_moves(self.game_state)44
        print("reset_state(): Permissible Moves: ", self.permissible_moves)
        self.done_moves = []
        self.draw_sub_buttons = []
        self.available_cards_for_steal_or_trade = []
        self.is_stealing = False
        self.is_trading = False
        self.selected_player_for_steal = None
        self.shuffle_sound_played = False
        # Reset all players' hide_hand flag
        for player in [self.game_state.current_player] + list(self.game_state.players):
            if player:
                player.hide_hand = False

    def restart_game(self):
        self.start_time = pygame.time.get_ticks()
        self.game_state.reset_state()
        self.create_players()
        self.deal_hands()
        self.choose_start_player()
        self.is_paused = False
        self.reset_state()

    def navigate_to_menu_screen(self):
        self.game_state.reset_state()
        return menuScreen(self.screen, self.game_state)

    def play_for_me_button(self):
        if self.game_state.current_player.type != PlayerType.HUMAN:
            return
        # Pretend we are a computer
        #self.game_state.current_player.type = self.game_state.computer_difficulty
        self.game_state.current_player.type = PlayerType.COMPUTER_HARD
        # Doing a computer turn
        if not self.computer_turn():
            # Somebody won, do not pass the turn to the next.
            self.game_state.current_player.type = PlayerType.HUMAN
            return
        # Returning the state back to human
        self.game_state.current_player.type = PlayerType.HUMAN
        self.trigger_end_turn()
        return

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
        text_x = panel_x + 90
        text_y = panel_y + 30 + self.guide_scroll

        start_y = panel_y + 30
        max_draw_y = panel_y + target_height - 30

        max_text_width = target_width - 180

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

    def draw_hidden_hand_icon(self, player, hand):
        hidden_img = self.deck.card_back
        count = len(player.hand)
        
      
        if not self.shuffle_sound_played:
            self.sound.playShuffle()
            self.shuffle_sound_played = True
        
      
        if hand.orientation == "vertical":
           
            rotated_img = pygame.transform.rotate(hidden_img, -90)
            spacing = -28  # Match vertical hand spacing (-18) + 10 extra pixels
            starty = hand.center_y - (spacing * (count - 1)) / 2
            x = hand.center_x
            for i in range(count):
                y = starty + i * spacing
                self.screen.blit(rotated_img, (x, y))
        else:
            # Horizontal display (top player)
            spacing = -28  # Match horizontal hand spacing (-18) + 10 extra pixels
            startx = hand.center_x - (spacing * (count - 1)) / 2
            y = hand.center_y
            for i in range(count):
                x = startx + i * spacing
                self.screen.blit(hidden_img, (x, y))

    def activate_trading(self):
        if self.is_stealing:
            self.is_trading = False
            return
        if self.is_trading:
            return
        self.is_trading = True
        # Re-using "card flying from the deck animation"
        self.draw_and_animate_cards(number_of_cards=1, player=self.game_state.current_player)

    def activate_stealing(self):
        if self.is_trading:
            self.is_stealing = False
            return
 
        # Exiting the stealing mode if it was pressed again, the implication in the draw function: getting rid of the text in draw objects if the steal mode has been activated 
        if self.is_stealing:
            self.is_stealing = False
            self.selected_player_for_steal = None
            # Reset hide_hand flags when canceling steal
            for player in [self.game_state.current_player] + list(self.game_state.players):
                if player:
                    player.hide_hand = False
            return
        self.is_stealing = True
        # To prevent subbuttons appearing after stealing was activated
        self.draw_sub_buttons = []
        self.selected_player_for_steal = None
        
        # For 2-player: Show card backs immediately when steal button is clicked
        if self.game_state.number_players == 2:
            all_players = [self.game_state.current_player] + list(self.game_state.players)
            for player in all_players:
                if player and player.player_id != self.game_state.current_player.player_id:
                    player.hide_hand = True
                    self.selected_player_for_steal = player
                    break
    
    def trigger_end_turn(self):
        pass_to_the_next = True
        # We can do recursion on itself after computer turn but we eliminate recursion with a flag and a while loop
        while pass_to_the_next:
            self.game_state.players.append(self.game_state.current_player)
            self.game_state.current_player = self.game_state.players.popleft()
            self.reset_state()
            self.permissible_moves = get_permissible_moves(self.game_state)
            if self.game_state.current_player.type != PlayerType.HUMAN:
                # If computer_turn returns true (if computer ended its turn and no one wins) -> we pass the turn to the next player (human or computer)
                # If computer_turn returns false - game stops (somebody won)
                pass_to_the_next = self.computer_turn()
            else:
                pass_to_the_next = False

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
        # to prevent the ability to activate stealing/trading if draw subbutons are active
        if self.is_stealing or self.is_trading:
            return
        self.draw_and_animate_cards(number_of_cards, player=self.game_state.current_player)
        self.draw_sub_buttons = []
        self.done_moves.append(PlayerMove.DRAW)

    # Animation for all cards movement
    def draw_and_animate_cards(self, number_of_cards, player):
        cards = self.game_state.deck.draw_cards(number_of_cards=number_of_cards)
        player.draw(cards)
        self.sound.playCardDraw()  
        for i in range(number_of_cards):
            # Overlay "trick" to show many cards being drawn from the deck
            self.deck.start_draw_animation(player.center_x + i * 20, player.center_y, speed=20.0)


    def create_players(self):
        self.game_state.players.clear()
        # players = deque()
        for i in range(self.game_state.number_players):
            if i == 0:
                self.game_state.players.append(Player(image=None, x=self.ui_hands[i].center_x, y=self.ui_hands[i].center_y, player_id=uuid.uuid4(), hand=[], player_type=PlayerType.HUMAN, name=f"Player {i}"))
            else:
                self.game_state.players.append(Player(image=None, x=self.ui_hands[i].center_x, y=self.ui_hands[i].center_y, player_id=uuid.uuid4(), hand=[], player_type=self.game_state.computer_difficulty, name=f"Player {i}"))
        # self.game_state.players = players
    
    # Finding the "real" first player index 
    def find_first_player_index(self, all_players) -> int:
        for i, player in enumerate(all_players):
            if player.name == "Player 0":
                return i

    def deal_hands(self):
        # Adding "flying cards" animation, using zip to match player with their hand position
        for player, hand in zip(self.game_state.players, self.ui_hands):
            self.draw_and_animate_cards(number_of_cards=4, player=player)
            
    
    def choose_start_player(self):
        self.game_state.current_player = self.game_state.players.popleft()

    def process_event(self, event):
        global current_screen
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not (self.showing_guide and event.button in [4, 5]):
                super().process_event(event)

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
        if self.game_state.current_player is not None and (len(self.game_state.current_player.hand) > 21 or (len(self.game_state.current_player.hand) == 21 and not self.is_trading)):
            raise ValueError(f"{self.game_state.current_player.name}'s hand exceeds 20 cards!")

        # print(f"proces_event(): {self.game_state.current_player.name} Permissible moves: {self.permissible_moves}")

        # Stealing
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_stealing:
            mouse_x, mouse_y = event.pos
            
            # For 3-player: Two-step process
            if self.game_state.number_players == 3:
               
                if self.selected_player_for_steal is None:
                    
                    all_players = [self.game_state.current_player] + list(self.game_state.players)
                    actual_first_player_index = self.find_first_player_index(all_players)
                    rotated_players = all_players[actual_first_player_index:] + all_players[:actual_first_player_index]
                    
                    if self.player2_rect.collidepoint(mouse_x, mouse_y) and len(rotated_players) > 1:
                        self.selected_player_for_steal = rotated_players[1]
                        self.selected_player_for_steal.hide_hand = True
                        return
                    
                    if self.game_state.number_players == 3 and self.player3_rect.collidepoint(mouse_x, mouse_y) and len(rotated_players) > 2:
                        self.selected_player_for_steal = rotated_players[2]
                        self.selected_player_for_steal.hide_hand = True
                        return
                        
           
                else:
                  
                    stolen_card = self.selected_player_for_steal.lose_card(random.randint(0, (len(self.selected_player_for_steal.hand)-1)))
                    self.game_state.current_player.take_card(stolen_card)
                    self.sound.playCardDraw()  
                    
                    
                    self.draw_objects()
                    pygame.display.update()
                    
                  
                    time.sleep(1) # pause before flipping cards back
                    
                    self.selected_player_for_steal.hide_hand = False
                    self.selected_player_for_steal = None
                    self.game_state.chosen_player = None
                    self.is_stealing = False
                    self.done_moves.append(PlayerMove.TAKE)
                    return
            
            else:

                if self.selected_player_for_steal is not None:
                    stolen_card = self.selected_player_for_steal.lose_card(random.randint(0, (len(self.selected_player_for_steal.hand)-1)))
                    self.game_state.current_player.take_card(stolen_card)
                    self.sound.playCardDraw()  
                    
                 
                    self.draw_objects()
                    pygame.display.update()
                    
                 
                    time.sleep(1)
                    
                    self.selected_player_for_steal.hide_hand = False
                    self.selected_player_for_steal = None
                    self.game_state.chosen_player = None
                    self.is_stealing = False
                    self.done_moves.append(PlayerMove.TAKE)
                    return
                
        # Trading
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_trading:
            mouse_x, mouse_y = event.pos
            for i, (card_vis, player, card) in enumerate(reversed(self.available_cards_for_steal_or_trade)): # needs to be changed
                if card_vis.contains_point(mouse_x, mouse_y):
                    handle_action_swap(self.game_state, None, None, lambda n=i: len(self.game_state.current_player.hand) - 1 - n, skip_drawing=True)
                    self.is_trading = False
                    self.done_moves.append(PlayerMove.DRAW_ONE)
                    return
        

        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.is_muted:
                if self.speaker_button.rect.collidepoint(event.pos):
                    self.toggle_sound()
                    return
            else:
                if self.mute_button.rect.collidepoint(event.pos):
                    self.toggle_sound()
                    return
            
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
                        screen = button.handle_event(event)
                        if screen is not None:
                            current_screen = screen
                            self.close = True
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
            for player in [self.game_state.current_player] + list(self.game_state.players):
                if player is None:
                    continue
                if len(player.hand) == 0:
                    print(f'The winner is {player.name}')
                    if player.name == 'Player 0':
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
        # player 0
        if self.game_state.current_player.name == "Player 0":
            self.screen.blit(self.stateArrow_surf, (620, 450))
        self.screen.blit(self.playerMe_surf, (600, 480))
        #player 2
        if self.game_state.current_player.name == "Player 1":
            self.screen.blit(self.stateArrow_surf, (620, 170))
        self.screen.blit(self.player2_surf, (600, 200))
        
        # 3 player (visual - steal mode)
        if self.game_state.number_players == 3:
            self.screen.blit(self.player3_surf, (230, 305))
        
        # Hover boxes - steal mode
        if self.is_stealing and self.selected_player_for_steal is None:
            mx, my = pygame.mouse.get_pos()
            if self.player2_rect.collidepoint(mx, my):
                pygame.draw.rect(self.screen, (255, 255, 0), self.player2_rect, 3)
            if self.game_state.number_players == 3 and self.player3_rect.collidepoint(mx, my):
                pygame.draw.rect(self.screen, (255, 255, 0), self.player3_rect, 3)
        
        if self.game_state.current_player.name == "Player 2":
            self.screen.blit(self.stateArrow_surf, (250, 275))

        self.permissible_moves = get_permissible_moves(self.game_state)
        for move in self.done_moves:
            if move in self.permissible_moves:
                self.permissible_moves.remove(move)
        self.deck.draw_deck(self.screen)
        self.deck.update_and_draw_animations(self.screen)
        
       
        if self.game_state.deck_shuffled and not self.showing_shuffle_animation:
            self.showing_shuffle_animation = True
            self.shuffle_animation_start_time = pygame.time.get_ticks()
            self.game_state.deck_shuffled = False
            self.sound.playShuffle() 
            
        
        # Shuffle animation
        if self.showing_shuffle_animation:
            time_passed = pygame.time.get_ticks() - self.shuffle_animation_start_time
            
            if time_passed < 2000:
              
                original_width = self.shuffle_gif.get_width()
                original_height = self.shuffle_gif.get_height()
                scaled_width = int(original_width * 0.8)
                scaled_height = int(original_height * 0.8)
                
              
                x_position = self.deck.rect.centerx - scaled_width // 2
                y_position = self.deck.rect.top - scaled_height - 10
                
             #gif bg 
                circle_radius = max(scaled_width, scaled_height) // 2 + 3
                circle_center = (self.deck.rect.centerx, y_position + scaled_height // 2)
                pygame.draw.circle(self.screen, (255, 255, 255), circle_center, circle_radius)
                
                # Render GIF on top
                temp_surface = pygame.Surface((original_width, original_height), pygame.SRCALPHA)
                self.shuffle_gif.render(temp_surface, (0, 0))
                scaled_surface = pygame.transform.scale(temp_surface, (scaled_width, scaled_height))
                self.screen.blit(scaled_surface, (x_position, y_position))
            else:
                self.showing_shuffle_animation = False

        sprites = CardSprites("cardsImages")
        for hand in self.ui_hands:
            hand.cards = []

        self.available_cards_for_steal_or_trade = []
        # Drawing all cards of all players
        mx, my = pygame.mouse.get_pos()

        all_players = [self.game_state.current_player] + list(self.game_state.players)
        # Finding the "real" first player
        actual_first_player_index = self.find_first_player_index(all_players)
        self.last_hand_visuals = []
        # Rotating so that the "real" first player is always at the bottom
        for i, player in enumerate(all_players[actual_first_player_index:]+all_players[:actual_first_player_index]):
                if i >= len(self.ui_hands):
                    break

                hand = self.ui_hands[i]
                hand.cards = []
                if player.hide_hand:
                    self.draw_hidden_hand_icon(player, hand)
                    continue

                player.sort_cards()
                for card_index, card in enumerate(player.hand):
                    card_vis = CardVisual(card.color.display_name, card.number, sprites)
                    
                    # If we are in the trading mode
                    if self.is_trading and player.player_id == self.game_state.current_player.player_id:
                        self.available_cards_for_steal_or_trade.append((card_vis, player, card))
                  
                    selected_state = self.card_states.get(card.id, False)
                    card_vis.selected = selected_state
                    # Regular hover (only when not in steal mode)
                    if not self.is_stealing and not self.is_trading:
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
           
            distance = (hand.center_x - self.deck.rect.centerx)**2 + (hand.center_y - self.deck.rect.centery)**2
            if pygame.time.get_ticks() - self.start_time > (distance)**0.5 / 1.1:
                hand.draw(self.screen)

        # Prompting the user to steal if it's stealing (relevant for human player)
        if self.is_stealing:
          
            if self.selected_player_for_steal is None:
                pygame.draw.rect(self.screen, (255, 255, 0), self.player2_rect, 6)
                if self.game_state.number_players == 3 and self.player3_rect:
                    pygame.draw.rect(self.screen, (255, 255, 0), self.player3_rect, 6)
            
            img_x = 640 - self.steal_m_surf.get_width() // 2
            img_y = 385
            self.screen.blit(self.steal_m_surf, (img_x, img_y))

        if self.is_trading:
            img_x = 640 - self.discard_m_surf.get_width() // 2
            img_y = 385 
            self.screen.blit(self.discard_m_surf, (img_x, img_y))

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
        
        if self.is_muted:
            self.mute_button.update(self.screen)
        else:
            self.speaker_button.update(self.screen)

        # To prevent cheating and bugs by ending the turn prematurely
        if not self.is_trading and not self.is_stealing:
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
        
    # Ensuring computer takes turns without the need to trigger any events
    # Takes a full computer turn
    def computer_turn(self):
        global current_screen

        # This is to make current player cursor (and other changes) visible 
        self.update_objects()
        self.draw_objects()
        pygame.display.update()

        if self.game_state.current_player.type != PlayerType.HUMAN:
            while True:
                # Wait for animations to finish before starting the next computer player move
                # Comment full if/else block if want to test all computers playing against each other
                if len(self.deck.animations) > 0:
                    self.update_objects()
                    self.draw_objects()
                    pygame.display.update()
                    continue
                # Wait for 200 msec for human eyes to understand the computer moves
                else:
                    pygame.time.wait(200)
                self.permissible_moves = get_permissible_moves(self.game_state)
                for move in self.done_moves:
                    if move in self.permissible_moves:
                        self.permissible_moves.remove(move)

                computer_player_decision = get_computer_player_decision(game_state=self.game_state, moves=self.permissible_moves)
                if len(self.permissible_moves) != 0:
                    move = computer_player_decision.choose()
                else:
                    raise ValueError("[Warning] Permissible moves cannot be empty!")
                print(f"{self.game_state.current_player.name} chose move: {move}")

                # Getting rid of the chosen buttons when computer player is playing (if it's not a discard button)
                if move in [PlayerMove.DRAW, PlayerMove.TAKE, PlayerMove.DRAW_ONE]:
                    self.done_moves.append(move)
                    self.update_objects()
                    self.draw_objects()
                    pygame.display.update()
  
                if move == PlayerMove.DRAW:
                    handle_action_draw_3(self.game_state, computer_player_decision, draw_animation=self.draw_and_animate_cards)

                if move == PlayerMove.TAKE:
                    handle_action_steal(self.game_state, computer_player_decision)

                if move == PlayerMove.DRAW_ONE:
                    handle_action_swap(self.game_state, computer_player_decision, draw_animation=self.draw_and_animate_cards)
                
                if move == PlayerMove.DISCARD_VALID_CARDS:
                    handle_action_discard_group(self.game_state)

                if move == PlayerMove.END_TURN or move == PlayerMove.PASS:
                    return True

                if not all_hands_non_empty(self.game_state):
                    for player in [self.game_state.current_player] + list(self.game_state.players):
                        if player is None:
                            continue
                        if len(player.hand) == 0:
                            print(f'The winner is {player.name}')
                            if player.name == 'Player 0':
                                self.game_state.state = State.WON
                            else:
                                self.game_state.state = State.LOST
                            is_endgame = True
                            break

                    self.game_state.reset_state()
                    current_screen = EndScreen(self.screen, self.game_state)
                    print(f"current screen:  {current_screen}")
                    self.close = True
                    return False

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
        super().process_event(event)
        
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

        self.sound.stopBackgroundMusic()
        if self.game_state.state == State.WON:
            self.sound.playWin()
        elif self.game_state.state == State.LOST:
            self.sound.playLose()
        
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
        self.sound.playBackgroundMusic()
        return playScreen(self.screen, self.game_state)

    def navigate_to_menu(self):
        self.sound.playBackgroundMusic()
        return menuScreen(self.screen, self.game_state)

    def update_objects(self):
        mouse_pos = pygame.mouse.get_pos()
        self.restart_button.changeColor(mouse_pos)
        self.backMenu_button.changeColor(mouse_pos)

    def process_event(self, event):
        global current_screen
        super().process_event(event)

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
