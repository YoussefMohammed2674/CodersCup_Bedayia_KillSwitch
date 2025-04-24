import pygame

pygame.mixer.init()
click_sound = pygame.mixer.Sound("sounds/click.mp3")
choose_sound = pygame.mixer.Sound("sounds/choose.mp3")
sound_on = True

def toggle_sound():
    global sound_on
    sound_on = not sound_on
    if sound_on:
        print("Sound ON")
    else:
        print("Sound OFF")