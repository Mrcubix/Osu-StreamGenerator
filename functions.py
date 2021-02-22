import pygame
from pygame import gfxdraw
from random import randint
import math
import numpy as np
import circles
import os
import pydub
import random

def generate_original_points_coordinates(display_res: list): # Generate original control points
    width = display_res[0]
    height = display_res[1]
    gen_points = []
    generating = True
    while generating:
        x = randint(0,width)
        y = randint(0,height)
        if y < 384 and y > 0  and x < 512 and x > 0:
            gen_points.append([x, y])
            generating = False
    return gen_points


def generate_points_coordinates(count: int, spacing: int, display_res: list, gen_points: list): # Genere more control points
    width = display_res[0]
    height = display_res[1]
    for i in range(0,count-1):
        generating = True
        while generating:
            x = gen_points[-1][0]+randint(-spacing,spacing)
            y = gen_points[-1][1]+randint(-spacing,spacing)
            if y < 384 and y > 0  and x < 512 and x > 0: 
                generating = False
                gen_points.append([x, y])
    return gen_points
        
        
def generate_original_and_p(count: int, spacing: int, display_res: list): # Parent fonction that generate both original and other points and return them under a list
    points = generate_original_points_coordinates(display_res)
    gen_points = generate_points_coordinates(count, spacing, display_res, points)
    return gen_points

#-------------- AbstractQbit functions ----------------------------#

def Lerp(A,B,alpha):    # ?
    return A*(1-alpha) + B * alpha


def Bezier(P1,P2,P3,alpha): # Generate bezier curve
    l1 = Lerp(P1, P3, alpha)
    l2 = Lerp(P3, P2, alpha)
    return Lerp(l1, l2, alpha)

#-------------------------------------------------------------------#


def Draw(surface: pygame.Surface, list_points, color_code: tuple, type: str, font=None, int=None):
    if type == "line":
        gfxdraw.line(surface, list_points[0], list_points[1], list_points[2], list_points[3], color_code)
    if type == "bezier":
        gfxdraw.bezier(surface, list_points, 4500, color_code)
    if type == "dot":
        gfxdraw.filled_circle(surface, list_points[0], list_points[1], 5, color_code)
        surface.blit(font.render(str(int), True, color_code), list_points)


def Generate_lines_and_curves(Points: list, is_acceleration_enabled, bpm, draw_line=False, screen=None, font=None):
    skip = 0
    curve = []
    for i in range(0,len(Points)-2):    #  Loop throught all positions

        dist_s = math.sqrt(math.pow(Points[i+2][0]-Points[i][0],2)+math.pow(Points[i+2][1]-Points[i][1],2))

        if skip:    # Skipping some iteration to avoid having 2 bezier on a cicle point
            skip = 0
            continue
        if dist_s < 234/2:  # If points are too close, then create a line
            line = []
            if draw_line:
                Draw(screen, [Points[i][0], Points[i][1], Points[i+2][0], Points[i+2][1]], (0,0,255), "line")
            skip=1

            #  Generate 1000 x coordinates / Generate 1000 y coordinates

            list_x, list_y = np.linspace(Points[i][0],Points[i+2][0],1000), np.linspace(Points[i][1],Points[i+2][1],1000)

            #  Generate a list of coordinates out of list_x and list_y

            line = [[round(list_x[i]),round(list_y[i])] for i in range(1000)]
            curve.append(line)

        else:   # Else Create a bezier curve
            if draw_line:
                Draw(screen, [Points[i], Points[i+1], Points[i+2]], (255,0,0), "bezier")
            curve.append(np.array([Bezier(np.array(Points[i]),np.array(Points[i+2]),np.array(Points[i+1]),a) for a in np.linspace(0,1,1000)]).tolist()) # Generate point on bezier curve
            skip = 1
        if i+2 == len(Points)-1 and draw_line:    # Make sure the last point is Drawn
            Draw(screen, [Points[i+2][0], Points[i+2][1]], (0,255,0), "dot", font, i)
        if draw_line:
            Draw(screen, [Points[i][0], Points[i][1]], (0,255,0), "dot", font, i) # Draw all points in screen for visualisation
    if is_acceleration_enabled:
        curve_acceleration = generate_acceleration(curve, is_acceleration_enabled, bpm)
        return (curve, curve_acceleration)
    return curve


def generate_acceleration(curve, Acceleration_settings, bpm):
    user_odds = Acceleration_settings[0][2]
    min_intensity_duration = Acceleration_settings[0][0]
    max_intensity_duration = Acceleration_settings[0][1]
    circle_space = Acceleration_settings[1]
    curve_acceleration = []
    curve_intensity = []
    count = 0
    for i in range(len(curve)):
        if random.randint(1,100) < user_odds:
            if random.randint(1,100) > 50:
                curve_intensity.append(0)
            else:
                curve_intensity.append(2)
        else:
            if curve_intensity:
                if curve_intensity[-1] == 0:
                    if count >= min_intensity_duration:
                        curve_intensity.append(1)
                        count=0
                        continue
                    else:
                        curve_intensity.append(0)
                        count += 1
                elif curve_intensity[-1] == 2:
                    if count >= max_intensity_duration:
                        curve_intensity.append(1)
                        count=0
                        continue
                    else:
                        curve_intensity.append(2)
                        count += 1
                else:
                    curve_intensity.append(1)
            else: 
                curve_intensity.append(random.randint(0,2))
    intensity_start_end = []
    for i in range(len(curve)):
        if i == 0:
            intensity_start = random.randint(0,2)
            a = (circle_space[curve_intensity[i]]-circle_space[intensity_start])/((60000/bpm)*len(curve[i])/1000)
            curve_acceleration.append(a)
            continue
        if i == len(curve_intensity)-1:
            intensity_end = random.randint(0,2)
            a = (circle_space[intensity_end]-circle_space[curve_intensity[-1]])/((60000/bpm)*len(curve[i])/1000)
            curve_acceleration.append(a)
            curve_intensity.append(intensity_end)
            continue
        else:
            a = (circle_space[curve_intensity[i+1]]-circle_space[curve_intensity[i]])/((60000/bpm)*len(curve[i])/1000)
        curve_acceleration.append(a)
    curve_intensity.insert(0,intensity_start)
    return (curve_acceleration, curve_intensity)


def Place_circles(curve, circle_space, cs, draw=True, screen=None):
    curve_acceleration = []
    if type(curve) == tuple:
        curve_acceleration = curve[1][0]
        curve_intensity = curve[1][1]
        curve = curve[0]
        #print(curve_intensity)
        #print(curve_acceleration)
    Circle_list = []
    idx = [0,0]
    for c in reversed(range(0,len(curve))):
        for p in reversed(range(0,len(curve[c]))):
            if not curve_acceleration and type(circle_space) == int:
                user_dist = circle_space
                dist = math.sqrt(math.pow(curve[c][p][0] - curve[idx[0]][idx[1]][0],2)+math.pow(curve [c][p][1] - curve[idx[0]][idx[1]][1],2))
                if dist > user_dist:
                    idx = [c,p]
                    Circle_list.append(circles.circles(round(curve[c][p][0]), round(curve[c][p][1]), cs, draw, screen))
            else:
                user_dist = circle_space[curve_intensity[c]] + curve_acceleration[c] * p
                dist = math.sqrt(math.pow(curve[c][p][0] - curve[idx[0]][idx[1]][0],2)+math.pow(curve [c][p][1] - curve[idx[0]][idx[1]][1],2))
                #print(user_dist)
                if dist > user_dist:
                    idx = [c,p]
                    Circle_list.append(circles.circles(round(curve[c][p][0]), round(curve[c][p][1]), cs, draw, screen))
                    #print(curve_intensity)
                    #print(curve_acceleration)
            
            
    return Circle_list


def osupath_prompt():
    prompt = True
    while prompt:
        osu_path = input("Insert osu folder path here: ")
        if os.path.isfile(os.path.abspath(osu_path + '/osu!.exe')):
            return osu_path


def bpm_prompt():
    prompt = True
    while prompt:
        bpm = input("Choose the stream map BPM: ")
        if bpm.isdigit():
            return str(round(int(bpm)))


def HPDrain_prompt():
    prompt = True
    while prompt:
        HP_Drain = input("HP Drain: ")
        if HP_Drain.replace('.','',1).isdigit():
            return HP_Drain


def CS_prompt(cs):
    prompt = True
    while prompt:
        if cs:
            i = input("would you like to re-define Circle Size? Y/n : ")
            if i == "Y" or i == "y":
                p_cs = input("CS: ")
                if p_cs.replace('.','',1).isdigit():
                    return str(p_cs)
            else:
                return str(cs)
        else:
            p_cs = input("CS: ")
            if p_cs.replace('.','',1).isdigit():
                return str(p_cs)


def OD_prompt():
    prompt = True
    while prompt:
        od = input("Overall Difficulty: ")
        if od.replace('.','',1).isdigit():
            return od


def AR_prompt():
    prompt = True
    while prompt:
        ar = input("Approach Rate: ")
        if ar.replace('.','',1).isdigit():
            return ar


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


def Write_Map(Circle_list, cs=None, osu_path=None, profile=None, audio=True):
    # Random Osu!StreamGenerator - 180bpm - 4 of 4
    if not osu_path:
        osu_path = osupath_prompt()
    if not profile:
        bpm = bpm_prompt()
        hp = HPDrain_prompt()
        cs = CS_prompt(cs)
        od = OD_prompt()
        ar = AR_prompt()
    else:
        bpm = profile["bpm"]
        hp = profile["hp"]
        cs = profile["cs"]
        od = profile["od"]
        ar = profile["ar"]

    timing = str(60000/int(bpm))
    os.listdir()
    if not os.path.exists(os.path.abspath(osu_path+"/Songs"+"/Random Osu!StreamGenerator - "+bpm+"bpm - 4 of 4")):
        os.makedirs(os.path.abspath(osu_path+"/Songs"+"/Random Osu!StreamGenerator - "+bpm+"bpm - 4 of 4"))
    map_path = os.path.abspath(osu_path+"/Songs"+"/Random Osu!StreamGenerator - "+bpm+"bpm - 4 of 4")
    list_number = []
    path = (os.path.abspath(osu_path+"/Songs"+"/Random Osu!StreamGenerator - "+bpm+"bpm - 4 of 4"))
    for file in os.listdir(path):
        if "n_" in file:
            list_number.append(file.split("n_")[1].split("]")[0])
    if not list_number:
        number = "0"
    else:
        number = str(len(list_number))
    with open(os.path.abspath(map_path+"/Osu!StreamGenerator - "+bpm+"bpm - 4 of 4 - (Osu!StreamGenerator) [Random n_"+number+"].osu"), "w") as f:
        f.write("osu file format v14\n\n")
        f.write("[General]\nAudioFilename: audio.mp3\nAudioLeadIn: 0\nPreviewTime: -1\nCountdown: 0\nSampleSet: Normal\nSampleSet: Normal\nStackLeniency: 0\nMode: 0\nLetterboxInBreaks: 0\nWidescreenStoryboard: 0\n\n")
        f.write("[Editor]\nDistanceSpacing: 1.9\nBeatDivisor: 4\nGridSize: 4\nTimelineZoom: 5.3\n\n")
        f.write("[Metadata]\nTitle:"+bpm+"bpm - 4/4\nTitleUnicode:"+bpm+"bpm - 4/4\nArtist:Osu!StreamGenerator\nArtistUnicode:Osu!StreamGenerator\nCreator:Osu!StreamGenerator\nVersion:Random n°"+number+"\nSource:Osu!StreamGenerator\nTags:Random random Osu!StreamGenerator osu!streamgenerator stream Stream "+bpm+"\nBeatmapID:0\nBeatmapSetID:-1\n\n")
        f.write("[Difficulty]\nHPDrainRate:"+hp+"\nCircleSize:"+cs+"\nOverallDifficulty:"+od+"\nApproachRate:"+ar+"\nSliderMultiplier:1.4\nSliderTickRate:1\n\n")
        f.write("[Events]\n//Background and Video events\n//Break Periods\n//Storyboard Layer 0 (Background)\n//Storyboard Layer 1 (Fail)\n//Storyboard Layer 2 (Pass)\n//Storyboard Layer 3 (Foreground)\n//Storyboard Layer 4 (Overlay)\n//Storyboard Sound Samples\n\n")
        f.write("[TimingPoints]\n0,"+timing+",4,1,0,100,1,0\n\n")
        f.write("[HitObjects]\n")
        for idx, circle in enumerate(Circle_list):
            f.write(str(circle.x)+","+str(circle.y)+","+str(5000+((idx+1)*(float(timing)/4)))+",1,0,0:0:0:0:\n")
    print(".osu Generation done")
    multiplier = int(bpm)/100
    if "audio.mp3" not in path and audio:
        track = pydub.AudioSegment.from_mp3(os.path.abspath(__file__.split("functions.py")[0]+"/assets/mp3/100bpm - 4 of 4.mp3"))
        track = track._spawn(track.raw_data, overrides={"frame_rate": int(track.frame_rate * multiplier)})
        track = track*2
        track.export(os.path.abspath(path+"/audio.mp3"), format="mp3", bitrate="192k")
    print("Done")
    return


            

