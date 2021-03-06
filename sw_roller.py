#!/usr/bin/env python3

import PySimpleGUIQt as sg
from random import randint
from decimal import Decimal
import json

sg.theme('Material1')
FONT_BASE_SIZE=14
FONT_HEADING=("Roboto", FONT_BASE_SIZE+4, "bold")
FONT_STAT=("Courier", FONT_BASE_SIZE, "bold")
FONT_SKILL=("Courier", FONT_BASE_SIZE-2)
FONT_BUTTON=("Roboto", FONT_BASE_SIZE)
FONT_BUTTON_EDIT=("Courier", FONT_BASE_SIZE+2)
FONT_BUTTON_NEW=("Roboto", FONT_BASE_SIZE-2)
FONT_RESULT=("Roboto", FONT_BASE_SIZE+10, "bold")
FONT_LOG=("Courier", FONT_BASE_SIZE-2)

MAX_RESULTS_LOG:"int" = 19

global character
character = {
    "stats": {
        "dex": {
            "name": "Dexterity",
            "value": '2.0',
            "skills": [
                {"key":"Blasters",     "value": '0.0'},
                {"key":"Dodge",        "value": '0.0'},
                {"key":"Heavy Weapons","value": '0.0'},
                {"key":"Melee",        "value": '0.0'},
                {"key":"Steal",        "value": '0.0'},
                {"key":"Throw",        "value": '0.0'},
            ]
        },
        "per": {
            "name": "Perception",
            "value": '2.0',
            "skills": [
                {"key":"Bargain","value": '0.0'},
                {"key":"Command","value": '0.0'},
                {"key":"Con",    "value": '0.0'},
                {"key":"Gamble", "value": '0.0'},
                {"key":"Stealth","value": '0.0'},
                {"key":"Search", "value": '0.0'},
            ]
        },
        "know": {
            "name": "Knowledge",
            "value": '2.0',
            "skills": [
                {"key":"Aliens",    "value": '0.0'},
                {"key":"Cultures",  "value": '0.0'},
                {"key":"Languages", "value": '0.0'},
                {"key":"Planets",   "value": '0.0'},
                {"key":"Streetwise","value": '0.0'},
                {"key":"Survivial", "value": '0.0'},
            ]
        },
        "str": {
            "name": "Strength",
            "value": '2.0',
            "skills": [
                {"key":"Athletics", "value": '0.0'},
                {"key":"Brawl",     "value": '0.0'},
                {"key":"Intimidate","value": '0.0'},
                {"key":"Lift",      "value": '0.0'},
                {"key":"Stamina",   "value": '0.0'},
                {"key":"Swim",      "value": '0.0'},
            ]
        },
        "mech": {
            "name": "Mechanical",
            "value": '2.0',
            "skills": [
                {"key":"Astrogation",    "value": '0.0'},
                {"key":"Beastriding",    "value": '0.0'},
                {"key":"Pilot: Repulsor","value": '0.0'},
                {"key":"Pilot: Starship","value": '0.0'},
                {"key":"Sensors",        "value": '0.0'},
                {"key":"Vehicle Weapons","value": '0.0'},
            ]
        },
        "tech": {
            "name": "Technical",
            "value": '2.0',
            "skills": [
                {"key":"Computer Tech","value": '0.0'},
                {"key":"Droid Tech",   "value": '0.0'},
                {"key":"Medicine",     "value": '0.0'},
                {"key":"Repulsor Tech","value": '0.0'},
                {"key":"Security",     "value": '0.0'},
                {"key":"Starship Tech","value": '0.0'},
            ]
        }
    },
    "weapons": [
        {"name":"Blaster","damage":"4.0"}
    ]
}

options = {
    "save":False,
    "edit":False,
    "filename": "",
    "modifier_advantage": '0.0',
    "modifier_penalty": '0.0',
}

results_log = []

def main():
    # Create the window
    global window
    window = make_window()

    # Create an event loop
    while True:
        event, values = window.read()
        # End program if user closes window or chooses Quit from menu
        if event in (sg.WIN_CLOSED, "Quit"):
            break

        # handle the desire to load from file
        if event in ("Load"):
            filename = sg.popup_get_file("Load Character Stats From File", title="Load Character", location=(100,0),file_types=(('JSON', '*.json'),('ALL Files', '*.*')))
            if filename and filename != '':
                options["filename"] = filename
                load_from_file()

        # save as
        if event == "Save As":
            filename = sg.popup_get_file("Save Character", title="Save Character", location=(100,0), save_as=True,file_types=(('JSON', '*.json'),('ALL Files', '*.*')),default_extension=".json")
            if filename and filename != '':
                if not filename.endswith(".json"):
                    filename = f"{filename}.json"
                options["filename"] = filename
                options["save"] = True
                window["-menu-"].update(menu_definition=make_menu())
                save_to_file()

        # save
        if event == "Save":
            save_to_file()

        # toggle edit mode
        if event == "Activate":
            options["edit"] = not options["edit"]
            window.close()
            window = make_edit_window()
        if event == "Deactivate":
            options["edit"] = not options["edit"]
            window.close()
            window = make_window()

        if event.startswith("ROLL."):
            handle_roll(event)

        if event.startswith("INC.STAT."):
            inc_stat(event)

        if event.startswith("DEC.STAT."):
            dec_stat(event)

        if event.startswith("INC.SKILL."):
            inc_skill(event)

        if event.startswith("DEC.SKILL."):
            dec_skill(event)

        if event.startswith("INC.WEAPON."):
            inc_weapon(event)

        if event.startswith("DEC.WEAPON."):
            dec_weapon(event)

        if event.startswith("REM.WEAPON."):
            rem_weapon(event)
            window.close()
            window = make_edit_window()

        if event.startswith("NEW.WEAPON"):
            new_weapon(event)
            window.close()
            window = make_edit_window()

        if event == "adv":
            options["modifier_advantage"] = f'{1.0 * values["adv"]}'
            window["curr_adv"].update(values["adv"])

        if event == "pen":
            options["modifier_penalty"] = f'{1.0 * values["pen"]}'
            window["curr_pen"].update(values["pen"])


    window.close()

def make_window() -> "sg.Window":
    global window
    window = sg.Window("SW Dice", layout=make_layout(), location=(0,0),resizable=True, finalize=True)
    return window

def make_menu() -> "list":
    menu_structure = []
    if options["save"]:
        menu_structure.append(['&File', ['&Load', '&Save', 'Save &As', '---', '&Quit']])
    else:
        menu_structure.append(['&File', ['&Load', '!&Save', 'Save &As', '---', '&Quit']])
    if options["edit"]:
        menu_structure.append(['&Edit Mode', ['&Deactivate']])
    else:
        menu_structure.append(['&Edit Mode', ['&Activate']])
    return menu_structure

def make_layout():
    layout = [
        [sg.Menu(make_menu(), key="-menu-")],
        [sg.Stretch(), sg.Text("Star Wars Dice Roller", font=FONT_HEADING), sg.Stretch()],
        [sg.HorizontalSeparator()]
    ]
    active = 0
    col_layout = [[],[]]
    for stat,val in character["stats"].items():
        col_layout[active].extend(make_stat_section(stat,val))
        if active == 0:
            active = 1
        else:
            active = 0
    layout.append([
        sg.Column(layout=col_layout[0]),
        sg.Column(layout=col_layout[1]),
        sg.Column(layout=[
            [sg.HorizontalSeparator(),],
            [
                sg.Stretch(),
                sg.Text(text="Action Modifiers", font=FONT_HEADING),
                sg.Stretch(),
            ],
            [
                sg.Text(text="Advantages",font=FONT_STAT),
                sg.Stretch(),
                sg.Slider(range=(0,5), default_value=0,orientation="h",size=(45, 10),key="adv",background_color="skyblue",enable_events=True),
                sg.Text(text="+",font=FONT_LOG),
                sg.Text(text="0", key="curr_adv",font=FONT_LOG),
                sg.Text(text="d",font=FONT_LOG),
            ],
            [
                sg.Text(text="Penalties",font=FONT_STAT),
                sg.Stretch(),
                sg.Slider(range=(0,5), default_value=0,orientation="h",size=(45, 10),key="pen",background_color="pink",enable_events=True),
                sg.Text(text="-",font=FONT_LOG),
                sg.Text(text="0", key="curr_pen",font=FONT_LOG),
                sg.Text(text="d",font=FONT_LOG),
            ],
            [sg.HorizontalSeparator(),],
            [sg.Text(text="Result", font=FONT_HEADING),sg.Stretch()],
            [sg.Text(text="Roll something!",key="-result-",font=FONT_RESULT,size_px=(650,100) , relief=sg.RELIEF_RIDGE)],
            [sg.HorizontalSeparator()],
            [sg.Text(text="Results Log", font=FONT_HEADING),sg.Stretch()],
            [sg.Text(text="",key="-resultlog-",font=FONT_LOG,relief=sg.RELIEF_SUNKEN)],
        ],size=(90,90)),
        sg.Column(layout=make_weapon_section(character["weapons"]))
    ])
    return layout

def make_stat_section(stat:"str",val:"dict") -> "list[sg.Element]":
    layout = []
    layout.append([
        sg.Text(f"{val['name']}",font=FONT_STAT),
        sg.Text(f"{' ' * (19 - len(val['name']))}",font=FONT_STAT),
        sg.Text(key=stat, text=display_as_dice(val["value"]),font=FONT_STAT),
        sg.Text(f"{' ' * (6 - len(display_as_dice(val['value'])))}",font=FONT_STAT),
        sg.Button("ROLL", key=f"ROLL.STAT.{stat}",font=FONT_BUTTON,button_color=("white","#0101ff"))

    ])
    for skill in val["skills"]:
        layout.append([
            sg.Text(f"  {skill['key']}",font=FONT_SKILL),
            sg.Text(f"{' ' * (21 - len(skill['key']))}",font=FONT_SKILL),
            sg.Text(key=f"{stat}.{skill['key']}", text=display_as_dice(skill["value"]),font=FONT_SKILL),
            sg.Text(f"{' ' * (4 - len(display_as_dice(skill['value'])))}",font=FONT_SKILL),
            sg.Button("ROLL", key=f"ROLL.SKILL.{stat}.{skill['key']}",font=FONT_BUTTON,button_color=("black","#55acee"))
        ])
    return layout

def make_weapon_section(weapons:"list[str]") -> "list[sg.Element]":
    layout = []
    layout.append([
        sg.Text("Weapons",font=FONT_HEADING)
    ])
    for idx, val in enumerate(weapons):
        layout.append([
            sg.Text(f"  {val['name']}",font=FONT_SKILL),
            sg.Text(f"{' ' * (19 - len(val['name']))}",font=FONT_SKILL),
            sg.Text(key=f"{val['name']}{idx}", text=display_as_dice(val["damage"]),font=FONT_SKILL),
            sg.Text(f"{' ' * (4 - len(display_as_dice(val['damage'])))}",font=FONT_SKILL),
            sg.Button("ROLL", key=f"ROLL.WEAPON.{idx}",font=FONT_BUTTON,button_color=("white","#ff0101"))
        ])
    return layout

# editing layout
def make_edit_window() -> "sg.Window":
    global window
    window = sg.Window("SW Dice", layout=make_edit_layout(), location=(0,0),resizable=True, finalize=True)
    return window

def make_edit_layout():
    layout = [
        [sg.Menu(make_menu(), key="-menu-")],
        [sg.Stretch(), sg.Text("Star Wars Dice Roller", font=FONT_HEADING), sg.Stretch()],
        [sg.HorizontalSeparator()]
    ]
    active = 0
    col_layout = [[],[]]
    for stat,val in character["stats"].items():
        col_layout[active].extend(make_edit_stat_section(stat,val))
        if active == 0:
            active = 1
        else:
            active = 0
    layout.append([
        sg.Column(layout=col_layout[0]),
        sg.Column(layout=col_layout[1]),
        sg.Column(layout=make_edit_weapons_section(character["weapons"]))
    ])
    return layout

def make_edit_stat_section(stat:"str",val:"dict") -> "list[sg.Element]":
    layout = []
    layout.append([
        sg.Text(f"{val['name']}",font=FONT_STAT),
        sg.Text(f"{' ' * (20 - len(val['name']))}",font=FONT_SKILL),
        sg.Text(key=stat, text=display_as_dice(val["value"]),font=FONT_STAT),
        sg.Button(" + ", key=f"INC.STAT.{stat}",font=FONT_BUTTON_EDIT,button_color=("black","lightgreen")),
        sg.Button(" - ", key=f"DEC.STAT.{stat}",font=FONT_BUTTON_EDIT,button_color=("black","pink")),
    ])
    for skill in val["skills"]:
        layout.append([
            sg.Text(f"   {skill['key']}",font=FONT_SKILL),
            sg.Text(f"{' ' * (19 - len(skill['key']))}",font=FONT_SKILL),
            sg.Text(key=f"{stat}.{skill['key']}", text=display_as_dice(skill["value"]),font=FONT_SKILL),
            sg.Text(f"{' ' * (4 - len(display_as_dice(skill['value'])))}",font=FONT_SKILL),
            sg.Button(" + ", key=f"INC.SKILL.{stat}.{skill['key']}",font=FONT_BUTTON_EDIT,button_color=("black","lightgreen")),
            sg.Button(" - ", key=f"DEC.SKILL.{stat}.{skill['key']}",font=FONT_BUTTON_EDIT,button_color=("black","pink")),
        ])
    return layout

def make_edit_weapons_section(weapons:"list[str]") -> "list[sg.Element]":
    layout = []
    layout.append([
        sg.Text("Weapons",font=FONT_HEADING)
    ])
    for idx, val in enumerate(weapons):
        layout.append([
            sg.Text(f"{val['name']}",font=FONT_SKILL),
            sg.Text(f"{' ' * (19 - len(val['name']))}",font=FONT_SKILL),
            sg.Text(key=f"{val['name']}{idx}", text=display_as_dice(val["damage"]),font=FONT_SKILL),
            sg.Text(f"{' ' * (4 - len(display_as_dice(val['damage'])))}",font=FONT_SKILL),
            sg.Button(" + ", key=f"INC.WEAPON.{idx}",font=FONT_BUTTON_EDIT,button_color=("black","lightgreen")),
            sg.Button(" - ", key=f"DEC.WEAPON.{idx}",font=FONT_BUTTON_EDIT,button_color=("black","pink")),
            sg.Button("X", key=f"REM.WEAPON.{idx}",font=FONT_BUTTON_EDIT,button_color=("black","red"))
        ])
    layout.append([
        sg.Stretch(),
        sg.Button("New Weapon", key=f"NEW.WEAPON",font=FONT_BUTTON_NEW,button_color=("black","lightblue"))
    ])
    return layout

def convert_to_dice_and_pips(score:'Decimal') -> 'list[int]':
    score_str = str(score) # deal with it as a string to split easier
    dice, pips = score_str.split('.')
    dice = int(dice)
    pips = int(pips)
    while pips > 2:
        dice += 1
        pips = pips - 3
    return [dice,pips]

def roll_dice(score:"Decimal") -> "int":
    dice, pips = convert_to_dice_and_pips(score)
    total:int = 0
    for _ in range(dice):
        total += randint(1,6)
    total += pips
    return total

def save_to_file():
    with open(options['filename'],'w') as fh:
        json.dump(character,fh,indent=2)

def load_from_file():
    global character
    with open(options['filename'],'r') as fh:
        character = json.load(fh)
    if "weapons" not in character:
        character["weapons"] = []
    options["save"] = True
    options["edit"] = False
    global window
    window.close()
    window = make_window()

def display_as_dice(score:"Decimal") -> "str":
    """
    display_as_dice takes a score like 1.2 and returns a string like 1d+2
    """
    dice, pips = convert_to_dice_and_pips(score)
    output = ""
    if dice > 0:
        output = f"{dice}d"
    else:
        output = "  "
    if pips > 0:
        output = f"{output}+{pips}"
    else:
        output = f"{output}  "
    if dice == 0 and pips == 0:
        output = " 0  "
    return output

def calculate_adjustment() -> "Decimal":
    return Decimal(options["modifier_advantage"]) - Decimal(options["modifier_penalty"])

def handle_roll(event:str):
    result:int = 0
    adjustment_total:Decimal = calculate_adjustment()
    if event.startswith("ROLL.SKILL."):
        _,_,stat,skill = event.split(".")
        # find the skill in the character data
        skill_value = '0.0'
        for s in character["stats"][stat]["skills"]:
            if s["key"] == skill:
                skill_value = s["value"]
                break
        result = roll_dice(Decimal(character["stats"][stat]["value"]) + Decimal(skill_value) + adjustment_total)
        record_result(f'{character["stats"][stat]["name"]}/ {skill}', result)
    elif event.startswith("ROLL.WEAPON."):
        _,_,idx = event.split(".")
        idx = int(idx)
        result = roll_dice(character["weapons"][idx]["damage"])
        record_result(f'{character["weapons"][idx]["name"]}',result)
    else: # must be a stat roll
        _,_,stat = event.split(".")
        result = roll_dice(Decimal(character["stats"][stat]["value"]) + adjustment_total)
        record_result(f'{character["stats"][stat]["name"]}',result)

def inc_stat(event:"str"):
    _,_,stat = event.split(".")
    new_score = Decimal(character["stats"][stat]["value"]) + Decimal('0.1')
    while int(str(new_score).split('.')[-1]) > 2:
        new_score += Decimal('0.7')
    character["stats"][stat]["value"] = str(new_score)
    window[stat].update(display_as_dice(new_score))

def dec_stat(event:"str"):
    _,_,stat = event.split(".")
    new_score = Decimal(character["stats"][stat]["value"]) - Decimal('0.1')
    while int(str(new_score).split('.')[-1]) > 2:
        new_score -= Decimal('0.7')
    if new_score < Decimal('0'):
        new_score = '0.0'
    character["stats"][stat]["value"] = str(new_score)
    window[stat].update(display_as_dice(new_score))

def inc_skill(event:"str"):
    _,_,stat,skill = event.split(".")
    for s in character["stats"][stat]["skills"]:
        if s["key"] == skill:
            new_score = Decimal(s["value"]) + Decimal('0.1')
            while int(str(new_score).split('.')[-1]) > 2:
                new_score += Decimal('0.7')
            s["value"] = str(new_score)
            window[f"{stat}.{skill}"].update(display_as_dice(new_score))
            break

def dec_skill(event:"str"):
    _,_,stat,skill = event.split(".")
    for s in character["stats"][stat]["skills"]:
        if s["key"] == skill:
            new_score = Decimal(s["value"]) - Decimal('0.1')
            while int(str(new_score).split('.')[-1]) > 2:
                new_score -= Decimal('0.7')
            if new_score < Decimal('0'):
                new_score = '0.0'
            s["value"] = str(new_score)
            window[f"{stat}.{skill}"].update(display_as_dice(new_score))
            break

def inc_weapon(event:"str"):
    _,_,idx = event.split(".")
    idx = int(idx)
    new_score = Decimal(character["weapons"][idx]["damage"]) + Decimal('0.1')
    while int(str(new_score).split('.')[-1]) > 2:
        new_score += Decimal('0.7')
    character["weapons"][idx]["damage"] = str(new_score)
    window[f"{character['weapons'][idx]['name']}{idx}"].update(display_as_dice(new_score))

def dec_weapon(event:"str"):
    _,_,idx = event.split(".")
    idx = int(idx)
    new_score = Decimal(character["weapons"][idx]["damage"]) - Decimal('0.1')
    while int(str(new_score).split('.')[-1]) > 2:
        new_score -= Decimal('0.7')
    if new_score < Decimal('0'):
        new_score = '0.0'
    character["weapons"][idx]["damage"] = str(new_score)
    window[f"{character['weapons'][idx]['name']}{idx}"].update(display_as_dice(new_score))

def rem_weapon(event:"str"):
    _,_,idx = event.split(".")
    idx = int(idx)
    character["weapons"].pop(idx)

def new_weapon(event:"str"):
    weapon = sg.popup_get_text("Weapon Name",
        title = "New Weapon",
        default_text = "Blaster",
        size = (90, None),
        button_color = None,
        background_color = None,
        text_color = None,
        icon = None,
        font = None,
        no_titlebar = False,
        grab_anywhere = False,
        keep_on_top = True,
        location = (0, 0)
    )
    character["weapons"].append({"name": weapon, "damage": "1.0"})

def record_result(pretty:"str",result:"int"):
    window['-result-'].update(f"{pretty}: {result}")
    results_log.insert(0,f"{pretty}: {result}")
    while len(results_log) > MAX_RESULTS_LOG:
        results_log.pop()
    window['-resultlog-'].update("\n".join(results_log))

if __name__ == "__main__":
    main()
