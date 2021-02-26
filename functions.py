import pygame
from pygame import *
from pygame import gfxdraw
import random
import math
import numpy as np
from pygame.draw import circle
import circles
import os
import pydub

def Generate_control_points(count):
    Control_points = []
    for i in range(count):
        generating = True
        if i == 0:
            while generating:
                x = random.randint(0,512)
                y = random.randint(0,384)
                if x >= 0 and x <= 512 and y >=0 and y <= 384:
                    generating = False
                    Control_points.append([x,y])
        else:
            while generating:
                x = Control_points[-1][0] + random.randint(-512,512)
                y = Control_points[-1][1] + random.randint(-384,384)
                if x >= 0 and x <= 512 and y >=0 and y <= 384:
                    generating = False
                    Control_points.append([x,y])
    return Control_points


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

def Generate_polyline_points(Control_points: list, dist_line_threshold: int  = 234, surface: Surface = None, DoDrawLine: bool = True, Font: bool = None):
    skip_points = False
    polyline = []
    for i in range(0,len(Control_points)-2):

        #--------------------------------------- Point Creation Section --------------------------------------#
        dist_b_control_points = math.sqrt((Control_points[i+2][0] - Control_points[i][0]) ** 2 + (Control_points[i+2][1] - Control_points[i][1]) ** 2)
        if skip_points: # Skipping some iteration to avoid having 2 bezier on a single point
            skip_points = False
            continue
        if dist_b_control_points < dist_line_threshold: #  If points are too close, then create a line
            line = []
            skip_points = True
            list_x, list_y = np.linspace(Control_points[i][0],Control_points[i+2][0],1000), np.linspace(Control_points[i][1],Control_points[i+2][1],1000) #  Generate 1000 x coordinates / Generate 1000 y coordinates
            line = [[round(list_x[i]),round(list_y[i])] for i in range(1000)] #  Generate a list of coordinates out of list_x and list_y
            polyline.append(line + ["line"]) #  Add type at the end of each curve for Draw()
        else:
            bezier_curve = (np.array([Bezier(np.array(Control_points[i]),np.array(Control_points[i+2]),np.array(Control_points[i+1]),a) for a in np.linspace(0,1,1000)]).tolist()) # Generate 1000 points on bezier curve
            polyline.append(bezier_curve + ["bezier"]) #  Add type at the end of each curve for Draw()
            skip_points = True
        #------------------------------------------- Drawing Section -------------------------------------------#
        if i+2 == len(Control_points)-1 and DoDrawLine:
            Draw(surface, [Control_points[i+2][0], Control_points[i+2][1]], (0,255,0), "dot", Font, i+2)
        if polyline[-1][-1] == "bezier" and DoDrawLine:
            Draw(surface, [Control_points[i], Control_points[i+1], Control_points[i+2]], (255,0,0), "bezier")
            Draw(surface, [Control_points[i][0], Control_points[i][1]], (0,255,0), "dot", Font, i)
            del polyline[-1][-1]
            continue
        elif DoDrawLine: 
            Draw(surface, [Control_points[i][0], Control_points[i][1], Control_points[i+2][0], Control_points[i+2][1]], (0,0,255), "line")
            Draw(surface, [Control_points[i][0], Control_points[i][1]], (0,255,0), "dot", Font, i)
            del polyline[-1][-1]
    if not DoDrawLine:
        for i in range(len(polyline)):
            del polyline[i][-1]
    return polyline


def ApplyAcceleration(Circle_list: list, circle_space: int, Args: list = None):
    curve_intensity = []
    spacings_per_curves = []
    if not Args or Args[0] == "NewProfile":
        prompt = True
        while prompt:
            max_duration_intensity = input("Choose the maximum amount of curve the change in intensity will occur for: ")
            if max_duration_intensity.isdigit():
                max_duration_intensity = int(max_duration_intensity)
                prompt = False
        prompt = True
        while prompt:
            intensity_change_odds = input("Choose the odds of occurence for changes in intensity (1-100): ")
            if intensity_change_odds.isdigit():
                intensity_change_odds = int(intensity_change_odds)
                if 0 < intensity_change_odds <= 100:
                    prompt = False      
        prompt = True
        while prompt:
            min_intensity = input("Choose the lowest amount of spacing a circle will have: ")
            if min_intensity.isdigit():
                min_intensity = float(min_intensity)
                if min_intensity < circle_space:
                    prompt = False 
        prompt = True
        while prompt:
            max_intensity = input("Choose the highest amount of spacing a circle will have: ")
            if max_intensity.isdigit():
                max_intensity = float(max_intensity)
                if max_intensity > circle_space:
                    prompt = False
        prompt = True
        while prompt:
            bpm = input("Choose the map BPM, necessary to apply intensity changes: ")
            if bpm.isdigit():
                bpm = int(bpm)
                prompt = False
        if Args:
            if Args[0] == "NewProfile":
                return [max_duration_intensity, intensity_change_odds, min_intensity, max_intensity]
            max_duration_intensity = 0
            intensity_change_odds = 0
            min_intensity = 0
            max_intensity = 0
            bpm = 0
    circle_space = ([min_intensity, circle_space, max_intensity] if not Args else [Args[2][0],circle_space,Args[2][2]])
    count = 0
    for idx, i in enumerate(Circle_list):
        if idx == len(Circle_list) - 1:
            if random.randint(0,100) < intensity_change_odds:
                if random.randint(0,100) > 50:
                    curve_intensity.append(2)
                else:
                    curve_intensity.append(0)
            else:
                 curve_intensity.append(1)
        if random.randint(0,100) < intensity_change_odds:
                if random.randint(0,100) > 50:
                    curve_intensity.append(2)
                    count += 1
                else:
                    curve_intensity.append(0)
                    count += 1
        else:
            if curve_intensity:
                if curve_intensity[-1] == 2 and not count+1 > max_duration_intensity:
                    curve_intensity.append(2)
                    count += 1
                    continue
                elif curve_intensity[-1] == 0 and not count+1 > max_duration_intensity:
                    curve_intensity.append(0)
                    count += 1
                    continue
                elif count+1 > 2:
                    curve_intensity.append(1)
                    count = 0
                    continue
                else:
                    curve_intensity.append(1)   
            else:
                curve_intensity.append(1)
    for i in range(len(curve_intensity)-1):
        if i+2 == len(curve_intensity):
            spacings_for_curve = np.linspace(circle_space[curve_intensity[i]],circle_space[curve_intensity[i+1]], len(Circle_list[i])).tolist()
            spacings_per_curves.append(spacings_for_curve)
            #print(spacings_for_curve)
            continue
        spacings_for_curve = np.linspace(circle_space[curve_intensity[i]],circle_space[curve_intensity[i+1]], len(Circle_list[i])).tolist()
        #print(spacings_for_curve)
        spacings_per_curves.append(spacings_for_curve)
    if curve_intensity.count(curve_intensity[0]) == len(curve_intensity):
        print("Intensity didn't change")
        return Circle_list
    print(curve_intensity)
    return spacings_per_curves

def Place_circles(polyline, circle_space, cs, DoDrawCircle=True, surface=None):
    Circle_list = []
    curve = []
    idx = [0,0]
    next_circle_space = None
    for c in reversed(range(0, len(polyline))):
        if type(circle_space) == list:
            iter_circle_space = iter(circle_space[c])
            next_circle_space = next(iter_circle_space)
            #print(circle_space[c])
        for p in reversed(range(0, len(polyline[c]))):
            dist = math.sqrt((polyline[c][p][0] - polyline[idx[0]][idx[1]][0]) ** 2 + (polyline [c][p][1] - polyline[idx[0]][idx[1]][1]) ** 2)
            if dist > (circle_space if type(circle_space) == int else next_circle_space):
                idx = [c,p]
                curve.append(circles.circles(round(polyline[c][p][0]), round(polyline[c][p][1]), cs, DoDrawCircle, surface))
                if type(circle_space) == list:
                    next_circle_space = next(iter_circle_space)
        Circle_list.append(curve)
    return Circle_list

def Acceleration_Prompt(Circle_list, circle_space):
    prompt = True
    while prompt:
        isAccelerationEnabled = input("Would you like to enable acceleration in streams? Y/n: ")
        if isAccelerationEnabled.isalpha():
            if (isAccelerationEnabled == "Y" or isAccelerationEnabled == "y"):
                Circle_list = ApplyAcceleration(Circle_list, circle_space)
                return Circle_list
            else:
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
    path = os.path.abspath(osu_path+"/Songs"+"/Random Osu!StreamGenerator - "+bpm+"bpm - 4 of 4")
    if not os.path.exists(path):
        os.makedirs(path)
    list_number = [] 
    for file in os.listdir(path):
        if "n_" in file:
            list_number.append(file.split("n_")[1].split("]")[0])
    if not list_number:
        number = "0"
    else:
        number = str(len(list_number))
    with open(os.path.abspath(path+"/Osu!StreamGenerator - "+bpm+"bpm - 4 of 4 - (Osu!StreamGenerator) [Random n_"+number+"].osu"), "w") as f:
        f.write("osu file format v14\n\n")
        f.write("[General]\nAudioFilename: audio.mp3\nAudioLeadIn: 0\nPreviewTime: -1\nCountdown: 0\nSampleSet: Normal\nSampleSet: Normal\nStackLeniency: 0.7\nMode: 0\nLetterboxInBreaks: 0\nWidescreenStoryboard: 0\n\n")
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
        track.export(os.path.abspath(path+"/audio.mp3"), format="mp3", bitrate="192k")
    print("Done")
    return