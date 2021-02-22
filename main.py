import pygame
from win32api import GetSystemMetrics
from functions import *
import sys

def count_prompt():  # Prompt user about number of points
    prompt = True
    while prompt:
        points_count = input("Count: ")
        if points_count.isdigit():
            return int(points_count)


def space_prompt():  # Prompt user for space between circles in px
    prompt = True
    while prompt:
        circle_space = input("Circle space: ")
        if circle_space.isdigit():
            return int(circle_space)


def line_prompt():
    prompt = True
    while prompt:
        i = input("Show lines? Y/n: ")
        if i.isalpha:
            if i == "Y" or i == "y":
                return True
            else:
                return False


def cs_prompt():
    prompt = True
    while prompt:
        cs = input("Circle Size: ")
        if cs.isdigit:
            return float(cs)


def acceleration_prompt():
    prompt = True
    while prompt:
        isenabled = input("Do you want to enable speed changes during streams? Y/n: ")
        if isenabled == "y" or isenabled == "Y":
            sub_prompt = True
            while sub_prompt:
                max_intensity_duration = input("Choose the maximum duration in curves for maximum intensity in int: ")
                if max_intensity_duration.isdigit():
                    max_intensity_duration = int(max_intensity_duration)
                    sub_prompt = False
            sub_prompt = True
            while sub_prompt:
                min_intensity_duration = input("Choose the maximum duration in curves for minimum intensity in int: ")
                if min_intensity_duration.isdigit():
                    min_intensity_duration = int(min_intensity_duration)
                    sub_prompt = False
            sub_prompt = True
            while sub_prompt:
                user_odds = input("Choose the odds of a decceleration and an acceleration to happen in int (1-100): ")
                if user_odds.isdigit():
                    user_odds = int(user_odds)
                    if 0 < user_odds < 101:
                        sub_prompt = False
            sub_prompt = True
            while sub_prompt:
                spacing_0 = input("Choose the lowest spacing spacing possible, a stream can have in pixels: ")
                print("minimum:",spacing_0)
                if spacing_0.isdigit():
                    spacing_0 = int(spacing_0)
                    spacing_2 = input("Choose the highest spacing possible, a stream can have in pixels: ")
                    print("maximum:",spacing_0)
                    if spacing_2.isdigit():
                        spacing_2 = int(spacing_2)
                        if spacing_2 > spacing_0:
                            spacing_1 = input("Choose a number between the max and the minimum, a stream can have in pixels: ")
                            print("middle:",spacing_1)
                            if spacing_1.isdigit():
                                spacing_1 = int(spacing_1)
                                if spacing_0 < spacing_1 < spacing_2:
                                    sub_prompt = False
        
            return ((min_intensity_duration , max_intensity_duration, user_odds),(spacing_0,spacing_1,spacing_2))
        else:
            return False


def bpm_prompt(acceleration_settings):
    if acceleration_settings:
        prompt = True
        while prompt:
            bpm = input("Choose the map bpm for map generation with acceleration: ")
            if bpm.isdigit():
                return int(bpm)

def screen_init(resolution):    # init screen
    screen = pygame.display.set_mode(resolution, 0, 32)
    screen.fill((33, 33, 33))
    return screen


def font_init():    # init font
    pygame.font.init()
    font = pygame.font.SysFont('freesansbold.ttf', 32)
    return font

width = GetSystemMetrics(0)
height = GetSystemMetrics(1)
resolution = [width, height]
Circle_list = []
#old_circle_list = []

#init corner
points_count = count_prompt()
circle_space = space_prompt()
draw_line = line_prompt()
acceleration_settings = ()
acceleration_settings = acceleration_prompt()
if acceleration_settings:
    circle_space = acceleration_settings[1]
bpm = bpm_prompt(acceleration_settings)
cs = cs_prompt()
screen = screen_init(resolution)
font = font_init()

running = True
while running:
    screen.fill((33, 33, 33))
    #if Circle_list and old_circle_list != Circle_list:
    #    pygame.draw.rect(screen, (22, 22, 22), (0,0,512,384))
    #    print("different")
    #    for circle in Circle_list:
    #        circle.Draw(screen)
    #old_circle_list = Circle_list
    #if Circle_list:
    #    if pygame.mouse.get_pressed()[0]:
    #        if Circle_list[0].isClicked():
    #            print("deleted")
    #            del Circle_list[0]
    # User input (NextAction)
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.type == pygame.QUIT:
                running = False
                sys.exit(0)
            if event.key == pygame.K_ESCAPE:
                running = False
                sys.exit(0)
            if event.key == pygame.K_SPACE:
                circle_space = space_prompt()
            if event.key == pygame.K_c:
                points_count = count_prompt()
            if event.key == pygame.K_RETURN:
                screen.fill((33, 33, 33))
                pygame.draw.rect(screen, (22, 22, 22), (0,0,512,384))
                curve = Generate_lines_and_curves(generate_original_and_p(points_count, 500, resolution), acceleration_settings, bpm, draw_line, screen, font)
                Circle_list = Place_circles(curve, circle_space, cs, screen=screen)
                pygame.display.update()
            if event.key == pygame.K_RSHIFT:
                screen.fill((33, 33, 33))
                pygame.draw.rect(screen, (22, 22, 22), (0,0,512,384))
                gen_points = generate_original_and_p(points_count, 500, resolution) # Generate points_counts points, spaced by at least 800 px (doesn't work), specify circle size to notappear off screen
                curve = Generate_lines_and_curves(gen_points, acceleration_settings, bpm, draw_line, screen, font)
                pygame.display.update()
            if event.key == pygame.K_w:
                if Circle_list:
                    print("Writing Map...")
                    Write_Map(Circle_list, cs)
    