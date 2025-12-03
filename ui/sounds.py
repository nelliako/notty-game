import pygame

class GameSound():
    def __init__(self):
        pygame.mixer.init()
        
        pygame.mixer.music.load('ui/soundsFile/bgmusic.mp3')
        pygame.mixer.music.set_volume(0.5)

        self.click_sound = pygame.mixer.Sound('ui/soundsFile/click.mp3')
        self.click_sound.set_volume(0.5)
        
        self.win_sound = pygame.mixer.Sound('ui/soundsFile/win.mp3')
        self.win_sound.set_volume(0.5)
        
        self.lose_sound = pygame.mixer.Sound('ui/soundsFile/lose.mp3')
        self.lose_sound.set_volume(0.5)

        pygame.mixer.music.play(-1)  # loop

    def playBackgroundMusic(self):
        pygame.mixer.music.play(-1)  #loop

    def stopBackgroundMusic(self):
        pygame.mixer.music.stop()
    
    def pauseBackgroundMusic(self):
        pygame.mixer.music.pause()
    
    def unpauseBackgroundMusic(self):
        pygame.mixer.music.unpause()

    def playClick(self):
        self.click_sound.play()
    
    def playWin(self):
        self.win_sound.play()
    
    def playLose(self):
        self.lose_sound.play()
