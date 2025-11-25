import pygame
import sys
from ui.button import Button
from ui.objects import imageObject
from ui.text_object import textObject

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
    def __init__(self, screen):
        super().__init__(screen)

        self.title = textObject(640, 220, "NOTTY", "Font/Minecraftia-Regular.ttf", 250, 'Black', 'center')

        self.background_surf = pygame.image.load("images/Vector.png").convert_alpha()

        button_surf = pygame.image.load("buttonImages/orangeButton.png").convert_alpha()
        button_surf = pygame.transform.scale(button_surf, (200, 50))

        button_font = pygame.font.Font("Font/Minecraftia-Regular.ttf", 20)
        self.play_button = Button(button_surf, 640, 450, "Play", button_font)
        self.options_button = Button(button_surf, 640, 530, "Options", button_font)
        self.exit_button = Button(button_surf, 640, 610, "Exit", button_font)

    def process_event(self, event):
        global current_screen
        if event.type == pygame.MOUSEBUTTONDOWN:
            #checkForInput
            click_pos = event.pos

            if self.play_button.checkForInput(click_pos):
                current_screen = playScreen(self.screen)
                self.close = True
                return

            if self.options_button.checkForInput(click_pos):
                current_screen = opSlectScreen(self.screen)
                self.close = True
                return

            if self.exit_button.checkForInput(click_pos):
                print("EXIT CLICKED")
                self.close = True
                current_screen = None
                return

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
    def __init__(self, screen):
        super().__init__(screen)

        self.is_paused = False
        center_x, center_y = 640, 360

        self.background_surf = pygame.image.load("images/Vector.png").convert_alpha()

        orangeButton_surf = pygame.image.load("buttonImages/orangeButton.png").convert_alpha()
        orangeButton_surf = pygame.transform.scale(orangeButton_surf, (100, 30))

        button_font = pygame.font.Font("Font/Minecraftia-Regular.ttf", 13)
        self.draw_button = Button(orangeButton_surf, 475, 340, "Draw", button_font)
        self.steal_button = Button(orangeButton_surf, 585, 340, "Steal", button_font)
        self.trade_button = Button(orangeButton_surf, 695, 340, "Trade", button_font)
        self.discard_button = Button(orangeButton_surf, 805, 340, "Discard", button_font)

        self.playForMe_button = Button(orangeButton_surf, 980, 40, "Play for me", button_font)
        self.guide_button = Button(orangeButton_surf, 1090, 40, "Guide", button_font)
        self.pause_button = Button(orangeButton_surf, 1200, 40, "Pause", button_font)

        self.resume_button = Button(orangeButton_surf, center_x, center_y - 80, "Resume", button_font)
        self.restart_button = Button(orangeButton_surf, center_x, center_y, "Restart", button_font)
        self.backMenu_button = Button(orangeButton_surf, center_x, center_y + 80, "Menu", button_font)
        self.overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 200))



    def process_event(self, event):
        global current_screen
        if event.type == pygame.MOUSEBUTTONDOWN:
            click_pos = event.pos

            if self.is_paused:
                if self.resume_button.checkForInput(click_pos):
                    self.is_paused = False
                elif self.restart_button.checkForInput(click_pos):
                    current_screen = playScreen(self.screen)
                    self.close = True
                    return
                elif self.backMenu_button.checkForInput(click_pos):
                    current_screen = menuScreen(self.screen)
                    self.close = True
                    return
            else:
                if self.pause_button.checkForInput(click_pos):
                    self.is_paused = True


            # if self.back_button.checkForInput(click_pos):
            #     current_screen = menuScreen(self.screen)
            #     self.close = True
            #     return
            #
            # if self.confirm_button.checkForInput(click_pos):
            #     self.close = True
            #     return


    def update_objects(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.is_paused:
            # Only update pause menu buttons when paused
            self.resume_button.changeColor(mouse_pos)
            self.restart_button.changeColor(mouse_pos)
            self.backMenu_button.changeColor(mouse_pos)
        else:
            self.draw_button.changeColor(mouse_pos)
            self.steal_button.changeColor(mouse_pos)
            self.trade_button.changeColor(mouse_pos)
            self.discard_button.changeColor(mouse_pos)
            self.playForMe_button.changeColor(mouse_pos)
            self.guide_button.changeColor(mouse_pos)
            self.pause_button.changeColor(mouse_pos)
        # self.player3_button.changeColor(mouse_pos)

    def draw_objects(self):
        self.screen.fill((212, 212, 212))
        self.screen.blit(self.background_surf, (0, 0))
        # self.select_frame.draw(self.screen)
        # self.title_options.draw(self.screen)
        # self.title_players.draw(self.screen)
        # self.title_level.draw(self.screen)

        self.draw_button.update(self.screen)
        self.steal_button.update(self.screen)
        self.trade_button.update(self.screen)
        self.discard_button.update(self.screen)
        self.playForMe_button.update(self.screen)
        self.guide_button.update(self.screen)
        self.pause_button.update(self.screen)
        # self.player3_button.update(self.screen)
        if self.is_paused:
            self.screen.blit(self.overlay, (0, 0))
            self.resume_button.update(self.screen)
            self.restart_button.update(self.screen)
            self.backMenu_button.update(self.screen)


class opSlectScreen(screenBase):
    def __init__(self, screen):
        super().__init__(screen)

        self.background_surf = pygame.image.load("images/Vector.png").convert_alpha()

        self.select_frame = imageObject("images/selectFrame.png", 640, 365, 'center')

        self.title_options = textObject(520, 135, "Options", "Font/Minecraftia-Regular.ttf", 35, 'Black', 'center')
        self.title_level = textObject(480, 200, "Choose level", "Font/Minecraftia-Regular.ttf", 35, 'Black', 'topleft')
        self.title_players = textObject(480, 390, "Players", "Font/Minecraftia-Regular.ttf", 35, 'Black', 'topleft')

        greenButton_surf = pygame.image.load("buttonImages/greenButton.png").convert_alpha()
        blueButton_surf = pygame.image.load("buttonImages/blueButton.png").convert_alpha()
        redButton_surf = pygame.image.load("buttonImages/redButton.png").convert_alpha()
        yellowButton_surf = pygame.image.load("buttonImages/yellowButton.png").convert_alpha()
        orangeButton_surf = pygame.image.load("buttonImages/orangeButton.png").convert_alpha()
        orangeButton_surf = pygame.transform.scale(orangeButton_surf, (100, 30))

        button_font = pygame.font.Font("Font/Minecraftia-Regular.ttf", 13)
        self.confirm_button = Button(orangeButton_surf, 660, 140, "Confirm", button_font)
        self.back_button = Button(orangeButton_surf, 770, 140, "Back", button_font)
        self.easy_button = Button(greenButton_surf, 520, 310, "Easy", button_font)
        self.medium_button = Button(blueButton_surf, 630, 310, "Medium", button_font)
        self.difficult_button = Button(redButton_surf, 740, 310, "Difficult", button_font)

        self.player1_button = Button(yellowButton_surf, 520, 500, "1 player", button_font)
        self.player2_button = Button(yellowButton_surf, 630, 500, "2 players", button_font)
        self.player3_button = Button(yellowButton_surf, 740, 500, "3 players", button_font)

    def process_event(self, event):
        global current_screen
        if event.type == pygame.MOUSEBUTTONDOWN:
            click_pos = event.pos

            if self.back_button.checkForInput(click_pos):
                current_screen = menuScreen(self.screen)
                self.close = True
                return

            if self.confirm_button.checkForInput(click_pos):
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
