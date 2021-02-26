import pygame
from pygame import display
from functions import *
import test
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

def screen_init(resolution):    # init screen
    screen = pygame.display.set_mode(resolution, 0, 32)
    screen.fill((33, 33, 33))
    return screen


def font_init():    # init font
    pygame.font.init()
    font = pygame.font.SysFont('freesansbold.ttf', 32)
    return font

pygame.init()
display_info = display.Info()
width = display_info.current_w
height = display_info.current_h
resolution = [width, height]
Circle_list = []
#old_circle_list = []

#init corner
points_count = count_prompt()
circle_space = space_prompt()
draw_line = line_prompt()
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
        if event.type == pygame.QUIT:
                running = False
                sys.exit(0)
        if event.type == pygame.KEYDOWN:  
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
                polyline = Generate_polyline_points(test.Generate_control_points(points_count), 117, screen, draw_line, font)
                Circle_list = Place_circles(polyline, circle_space, cs, surface=screen)
                spacings_per_curves = Acceleration_Prompt(Circle_list, circle_space)
                if spacings_per_curves != Circle_list:
                    screen.fill((33, 33, 33))
                    old_Circle_list = Circle_list
                    Circle_list = Place_circles(polyline, spacings_per_curves, cs, surface=screen)
                    Circle_dict = {}
                    for idx, i in enumerate([old_Circle_list, Circle_list]):
                        Circle_dict.update({"List"+str(idx): []})
                        for curves in i:
                            for circles in curves:
                                Circle_dict["List"+str(idx)].append(circles.GetPos())
                    if Circle_dict["List0"] == Circle_dict["List1"]:
                        print("same")
                pygame.display.update()
            if event.key == pygame.K_RSHIFT:
                screen.fill((33, 33, 33))
                pygame.draw.rect(screen, (22, 22, 22), (0,0,512,384))
                # Generate points_counts points, spaced by at least 800 px (doesn't work), specify circle size to notappear off screen
                Control_Points = Generate_control_points(points_count)
                polyline = Generate_polyline_points(Control_Points, 117, screen, draw_line, font)
                pygame.display.update()
            if event.key == pygame.K_w:
                if Circle_list:
                    print("Writing Map...")
                    Write_Map(Circle_list, cs)
    