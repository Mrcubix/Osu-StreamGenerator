import os
import functions
import sys
import json
import base64
from win32api import GetSystemMetrics


def profile_prompt():
    name = input("Choose the new profile's name: ")
    name = str(base64.b64encode(name.encode('ascii')))[2:-1]
    bpm = functions.bpm_prompt()
    hp = functions.HPDrain_prompt()
    cs = functions.CS_prompt(None)
    od = functions.OD_prompt()
    ar = functions.AR_prompt()
    prompt = True
    while prompt:
        control_points_c = input("Control Points Count: ")
        if control_points_c.isdigit():
            prompt = False
    prompt = True
    while prompt:
        spacing = input("Spacing between circles in px: ")
        if spacing.isdigit():
            prompt = False
    return {"default": name, name: {"bpm": bpm,"hp": hp, "cs": cs, "od": od, "ar": ar, "control_point_c": control_points_c, "spacing": spacing}}


def isfirststart():
    if not os.path.exists(__file__.split("batch_gen.py")[0]+"settings.json"):
        osu_path = functions.osupath_prompt()
        osu_path = str(base64.b64encode(osu_path.encode("ascii")))[2:-1]
        print("Info: As this is the first time opening this file, you're required to create a new profile for your first batch.")
        profile = profile_prompt()
        settings = {"osu_path": osu_path}
        settings.update(profile)
        print(settings)
        with open("settings.json", "w") as f:
            json.dump(settings,f)
        print("Now restart this script and you should be good to go!")
        return True
    return False


width = GetSystemMetrics(0)
height = GetSystemMetrics(1)
resolution = [width, height]

args = sys.argv[1:]

Circle_list = []

def gen_maps(args,number=1):
    if args:
        if "-first_start" in args or "-fs" in args:
            isfirststart()
        if "-gen" in args:
            if not isfirststart():
                with open("settings.json", "r") as f:
                    data = json.load(f)
                if "-p" not in args:
                    default = data["default"]
                    profile = data[default]
                count = int(profile["control_point_c"])
                cs = profile["cs"]
                spacing = int(profile["spacing"])
                if "-noaudio" in args:
                    audio = False
                else:
                    audio = True
                osu_path = str(base64.b64decode(bytes(data["osu_path"].encode("ascii"))))[2:-1]
                for i in range(0,number):
                    curve = functions.Generate_lines_and_curves(functions.generate_original_and_p(count, 500, resolution), False)
                    Circle_list = functions.Place_circles(curve, spacing, cs, draw=False)
                    functions.Write_Map(Circle_list, profile=profile, audio=audio, osu_path=osu_path)
                    print(str(i+1)+"/"+str(number)+" Completed")
    else:
        print("No arguments provided")

if not args:
    args.append("-gen")
prompt = True
if "-n" not in args:
    while prompt:
        number = input("Enter the number of maps to generate: ")
        if number.isdigit():
            number = int(number)
            prompt = False
elif args[args.index("-n")+1].isdigit():
    number = args[args.index("-n")+1]
else:
    print("Incorrect value for -n")
    exit()
    
gen_maps(args,number)
        


