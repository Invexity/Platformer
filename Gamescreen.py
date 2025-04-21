"""

  _______ _ _   _         _____
 |__   __(_) | | |       / ____|
    | |   _| |_| | ___  | (___   ___ _ __ ___  ___ _ __
    | |  | | __| |/ _ \  \___ \ / __| '__/ _ \/ _ \ '_ \
    | |  | | |_| |  __/  ____) | (__| | |  __/  __/ | | |
    |_|  |_|\__|_|\___| |_____/ \___|_|  \___|\___|_| |_|


"""
import json, pygame, math, os, time
from sys import exit

from classes import Button

pygame.display.set_caption('Jumpy')
screen_x = 1920
screen_y = 1080
Gameloop = 0
os.environ['SDL_AUDIODRIVER'] = 'dsp'
pygame.init()
pygame.font.init()
window = pygame.display.set_mode((screen_x, screen_y))

button_image = pygame.image.load("button3.png").convert_alpha()
start_button = Button(screen_x/2 - 200, screen_y/2 + 100, button_image, 0.3)

outline = pygame.image.load("button2.png").convert_alpha()
outline_scaled = pygame.transform.scale(outline, (screen_x/4 + 270, screen_y/4 + 100))
outline_pos = screen_x/3 - 70, screen_y/4 - 10

background_image = pygame.image.load("background.png").convert_alpha()
background_scaled = pygame.transform.scale(background_image, (screen_x,screen_y))
background_pos = 0,0

font = pygame.font.SysFont('Comic Sans MS', 200)
text_surface = font.render('Jumpy', False, (0,0,0))
text_pos = screen_x/4+170, screen_y/4

font = pygame.font.SysFont('Comic Sans', 90)
text_start = font.render('Start', False, (0,0,0))
text_pos2 = screen_x/2 - 140, screen_y/2 + 110

fade_surface = pygame.Surface((screen_x, screen_y))
fade_surface.fill((0, 0, 0))  # Set the fade color (black)
fade_alpha = 0  # Start with 0 alpha (completely transparent)

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # if event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_SPACE:
        #         run = False

    window.blit(background_scaled, background_pos)
    pygame.draw.rect(window, (64, 64, 64), (screen_x / 4, screen_y / 4, screen_x / 2, screen_y / 2), 0, 100)
    window.blit(outline_scaled, outline_pos)
    window.blit(text_surface, text_pos)

    if start_button.draw(window):
        Gameloop = 1
        #run = False

    if Gameloop == 1:  # If the start button was pressed, start fading.
        fade_alpha += 5  # Increase alpha for fade effect
        if fade_alpha >= 255:
            fade_alpha = 255  # Ensure it doesn't exceed max value
            Gameloop = 2
            run = False # Transition to the next game screen (you can place your game logic here)

        fade_surface.set_alpha(fade_alpha)  # Set the fade surface transparency
        window.blit(fade_surface, (0, 0))  # Apply the fade effect on the screen


    window.blit(text_start, text_pos2)

    pygame.display.update()