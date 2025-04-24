import pygame
import ctypes
from menu import Menu

user32 = ctypes.windll.user32
screen_w = user32.GetSystemMetrics(0)
screen_h = user32.GetSystemMetrics(1)

def launch_game():
    pygame.init()

    win = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Main Menu")

    menu = Menu(win)
    menu.run()

    pygame.quit()

if __name__ == "__main__":
    launch_game()