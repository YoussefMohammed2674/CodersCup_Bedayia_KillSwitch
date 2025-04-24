import pygame
from story_cutscene import show_cutscene

def start_story_mode(player_char):
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    name_font = pygame.font.Font("fonts/PressStart2P.ttf", 22)
    font = pygame.font.Font("fonts/PressStart2P.ttf", 18)

    show_cutscene(screen, clock, font, name_font)

