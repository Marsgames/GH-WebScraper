# coding: utf-8

import requests
import time
import os
import difflib
import re
import pathlib
# import json

from bs4 import BeautifulSoup


wowClassesUrl = "https://wowwiki.fandom.com/wiki/SpecializationID"
# get current path
path = f"{pathlib.Path(__file__).parent.resolve()}/"
# path = "/Users/Raph/Documents/HE/WebScraping/"
# path = "/Users/rd-headcrab/Library/Mobile Documents/com~apple~CloudDocs/Documents/HE/WebScraping/"
# path = ""
linksDic = {}
response = None
f1_text = ""
f2_text = ""


def GetClasses():
    global wowClassesUrl
    global linksDic
    global response

    response = requests.get(wowClassesUrl)
    if not response.ok:
        exit()

    soup = BeautifulSoup(response.text, "html.parser")
    dl = soup.find("dl")

    lines = str(dl.text).splitlines()
    classNames = -1
    id = -1
    spec = -1
    # Get from wowwiki ClassName, SpecID and SpecName
    for line in lines:
        line = line.strip()
        line = line.replace(" ", "-")
        if not line[0].isdigit():
            classNames = line
        else:
            id = line.split("-")[0]
            spec = line.split("-")[-1]
            linksDic[id] = (classNames, spec)


def CleanPawnString(pawnString):  # -> str:
    pawnString = pawnString.replace("HasteRating", "Haste")
    pawnString = pawnString.replace("CritRating", "CriticalStrike")
    pawnString = pawnString.replace("MasteryRating", "Mastery")
    pawnString = pawnString.replace("DPS", "MainHandDps")
    pawnString = pawnString.replace("OffHandDPS", "OffHandDps")

    return pawnString


def GenerateGHStringFromPawn(pawnDict):  # -> str:
    # if pawnDict doesn't contains a key named "Intellect"
    ghString = ""
    if pawnDict.get("Intellect"):
        ghString += f"ITEM_MOD_INTELLECT_SHORT = {pawnDict['Intellect']},\n"
    if pawnDict.get("Haste"):
        ghString += f"ITEM_MOD_HASTE_RATING_SHORT = {pawnDict['Haste']},\n"
    if pawnDict.get("CriticalStrike"):
        ghString += f"ITEM_MOD_CRIT_RATING_SHORT = {pawnDict['CriticalStrike']},\n"
    if pawnDict.get("Versatility"):
        ghString += f"ITEM_MOD_VERSATILITY = {pawnDict['Versatility']},\n"
    if pawnDict.get("Mastery"):
        ghString += (
            "ITEM_MOD_MASTERY_RATING_SHORT = " +
            str(pawnDict["Mastery"]) + ",\n"
        )
    if pawnDict.get("Agility"):
        ghString += "ITEM_MOD_AGILITY_SHORT = " + \
            str(pawnDict["Agility"]) + ",\n"
    if pawnDict.get("Stamina"):
        ghString += "ITEM_MOD_STAMINA_SHORT = " + \
            str(pawnDict["Stamina"]) + ",\n"
    if pawnDict.get("Strength"):
        ghString += "ITEM_MOD_STRENGTH_SHORT = " + \
            str(pawnDict["Strength"]) + ",\n"

    if pawnDict.get("MainHandDps"):
        ghString += "MainHandDps " + str(pawnDict["MainHandDps"]) + ",\n"
    if pawnDict.get("OffHandDps"):
        ghString += "OffHandDps " + str(pawnDict["OffHandDps"]) + ",\n"

    return ghString[:-3]


def GenerateGHStringFromStats(datasList):
    ghString = ""
    for data in datasList:
        data = data.replace(" ", "")
        data = data.replace("[", "")
        try:
            stat, value = data.split(">")
            # print(f"stat:<{stat}>\nvalue: <{value}>\n")
            if stat == "Intellect":
                ghString += f"            [ITEM_MOD_INTELLECT_SHORT] = {value},\n"
            if stat == "Haste":
                ghString += f"            [ITEM_MOD_HASTE_RATING_SHORT] = {value},\n"
            if stat == "Crit":
                ghString += f"            [ITEM_MOD_CRIT_RATING_SHORT] = {value},\n"
            if stat == "Versatility":
                ghString += f"            [ITEM_MOD_VERSATILITY] = {value},\n"
            if stat == "Mastery":
                ghString += f"            [ITEM_MOD_MASTERY_RATING_SHORT] = {value},\n"
            if stat == "Agility":
                ghString += f"            [ITEM_MOD_AGILITY_SHORT] = {value},\n"
            if stat == "Stamina":
                ghString += f"            [ITEM_MOD_STAMINA_SHORT] = {value},\n"
            if stat == "Str":
                ghString += f"            [ITEM_MOD_STRENGTH_SHORT] = {value},\n"
            if stat == "Attack-Power":
                ghString += f"            [ITEM_MOD_ATTACK_POWER_SHORT] = {value},\n"
            if stat == "Armor":
                ghString += f"            [ARMOR] = {value},\n"
            if stat == "Bonus-Armor":
                ghString += f"            [ITEM_MOD_EXTRA_ARMOR_SHORT] = {value},\n"
            if stat == "Leech":
                ghString += f"            [ITEM_MOD_CR_LIFESTEAL_SHORT] = {value},\n"
            if stat == "Spell-Power":
                ghString += f"            [ITEM_MOD_SPELL_POWER_SHORT] = {value},\n"
            if stat == "Weapon-Dps":
                ghString += f"            [ITEM_MOD_DAMAGE_PER_SECOND_SHORT] = {value},\n"
        except:
            pass

    return ghString


def GetNoxxicStats():
    global wowClassesUrl
    global path
    global linksDic
    global response

    # Create a file named "part2" wich will contain noxxic stats
    with open(str(path) + "part2.txt", "w") as file:
        # Foreach spec, create a noxxic link
        for item in linksDic.items():
            className = item[1][0]
            specName = item[1][1]
            if (
                "mastery" == specName.lower()
            ):  # This is bad, modify scrapper to get right name !
                specName = "beast-mastery"
            specID = str(item[0])
            wowClassesUrl = (
                "https://www.noxxic.com/wow/guide/"
                + specName
                + "-"
                + className
                + "/stat-priority/"
            ).lower()

            print("url : " + str(wowClassesUrl))

            # Try to connect to noxxic link previously created
            response = requests.get(wowClassesUrl)
            if not response.ok:
                continue

            # print("response : " + str(response.text))

            ##### BF4 ne marche plus, alternative : #####
            # regex = r"Stat Weights[a-zA-Z ()0-9.\\=-]+"
            # "stat_weights":{"stamina":-0.05,"attack power":3.34,"mastery":3.83,"versatility":4.23,"haste":3,"armor":-0.05,"bonusarmor":-0.04,"weapon dps":20.34,"leech":-0.06,"str":6.19,"crit":4.29}
            regex = r'"stat_weights":{.*?}'

            # Only keep regex matching parts of response.text
            match = re.search(regex, response.text)
            # print(f"match : {match.group(0)}")
            stats = match.group(0)

            # remove last 8 chars from stats
            # stats = stats[:-8]
            # stats = stats[47:]
            stats = stats.replace('"stat_weights":{', "")
            stats = stats.title()
            stats = stats.replace("}", "")
            stats = stats.replace('"', "")
            stats = stats.replace(":", " > [")
            stats = stats.replace(",", "] ")
            # replace all "\u003e" by ">"
            stats = stats.replace("\\u003e", ">")

            stats = stats.replace("Weapon Offhand Dps", "OffHandDps")
            stats = stats.replace("Weapon Dps", "Weapon-Dps")
            stats = stats.replace("Attack Power", "Attack-Power")
            stats = stats.replace("Spell Power", "Spell-Power")
            stats = stats.replace("Bonusarmor", "Bonus-Armor")
            stats = stats.replace("str", "Strength")
            stats += "]"

            # string format = Crit > [4.77] Haste > [5.67] Mastery > [4.57] Stamina > [9.07] Str > [7.57] Versatility > [6.01]
            statsString = stats
            stats = str.split(statsString, "]")
            statsString = GenerateGHStringFromStats(stats)

            # stats = stats.replace("Attack Power", "OffHandDps")

            # print("stats : " + str(stats))
            # exit()
            ##########

            # Fut un temps, BF4 marchait
            # soup = BeautifulSoup(response.text, "html.parser")
            # bubbles = soup.find_all("div")

            # If stats exists, add them to the file, formated for GH
            # if len(bubbles) > 1:
            #     bubble = bubbles[1].text

            file.write(
                "    -- "
                + className.upper().replace("-", " ")
                + " "
                + specName.upper().replace("-", " ")
                + " --\n"
            )
            file.write("    [" + str(specID) + "] = {\n")

            ##### Alternative à BF4 : #####
            file.write('        ["NOX"] = {\n' + statsString + "        }\n")
            # print(f"{className} - {specName} : {str(stats)}")
            ##########

            ##### BF4 #####
            # if len(bubbles) > 2:  # Si les stats sont présentes
            #     file.write(
            #         '        ["NOX"] = "'
            #         + str(bubble)
            #         .replace("&gt;", ">")
            #         .replace("(", "[")
            #         .replace(")", "]")
            #         + '"\n'
            #     )
            # else:  # Sinon on parse la pawn string
            #     # Parse pawn string
            #     # {Class:Priest, Spec:Holy, Intellect:7.52, HasteRating:6.11, CritRating:5.72, Versatility:5.72, MasteryRating:5.11}

            #     # replace char at index 10 from bubble by ","
            #     bubble = bubble[:10] + "," + bubble[11:]
            #     bubble = bubble.replace("=", ":")

            #     # Format bubble string to a dict compatible
            #     bubble = re.sub(r", \".+: ", ",", bubble)
            #     bubble = re.sub(r"(\w+):", r'"\1":', bubble)
            #     bubble = re.sub(r"([A-z]+),", r'"\1",', bubble)
            #     bubble = '{"' + bubble[bubble.find("C") : -1] + "}"

            #     bubble = CleanPawnString(bubble)

            #     # string to dict
            #     bubble = json.loads(bubble)

            #     ghString = GenerateGHStringFromPawn(bubble)

            #     file.write('        ["NOX"] = "' + ghString + '"\n')
            ##########

            file.write("    },\n")
        file.write("}\n")
        time.sleep(1)


def CreateWeightValuesFile():
    global path
    global f1_text
    global f2_text

    # Concatenate files part1, part2 and part3
    filenames = [
        str(path) + "part1.txt",
        str(path) + "part2.txt",
        str(path) + "part3.txt",
    ]
    with open(str(path) + "StatsActuelles.txt", "w") as StatsActuelles:
        for parts in filenames:
            with open(parts) as infile:
                StatsActuelles.write(infile.read())

    # Remove file part2 (the one created with noxxic values)
    os.remove(str(path) + "part2.txt")

    # Remove return if we want to checkdiff
    return
    with open(str(path) + "StatsActuelles.txt") as f1:
        f1_text = f1.read()
    with open(
        "/Applications/World of Warcraft/_retail_/Interface/AddOns/GearHelper/WeightValues.lua"
    ) as f2:
        f2_text = f2.read()


def CheckDiff():  # -> bool:
    global f1_text
    global f2_text

    # Find differences
    diffs = 0

    for line in difflib.unified_diff(
        f1_text, f2_text, fromfile="file1", tofile="file2", lineterm=""
    ):
        diffs += 1

    # The notifier function
    def notify(title, message):
        # This requires a mac + terminal-notifier + the right path
        # Do not call this function if you do not need it
        os.system(
            'terminal-notifier -title "'
            + title
            + '" -message "'
            + message
            + '" -activate com.apple.Terminal -execute "wdiff /Applications/World\ of\ Warcraft/_retail_/Interface/AddOns/GearHelper/WeightValues.lua /Users/Raph/Documents/GH/statsAJour.txt | colordiff" -appIcon "https://media.forgecdn.net/avatars/thumbnails/54/445/64/64/636135209663914354.png"'
        )

    # Show notification if any diff
    if diffs > 0:
        # Calling the function
        notify(title="GearHelper", message="Les stats Noxxic ont changées !!")
        return True
    return False


def RemoveUnusedFiles():
    global path

    # Remove unused files
    os.system(
        "cp " + str(path) + "StatsActuelles.txt " +
        str(path) + "WeightValues.lua"
    )
    os.remove(str(path) + "StatsActuelles.txt")
    os.remove(
        "/Applications/World of Warcraft/_retail_/Interface/AddOns/GearHelper/WeightValues.lua"
    )
    os.system(
        "cp "
        + str(path)
        + "WeightValues.lua "
        + "/Applications/World\ of\ Warcraft/_retail_/Interface/AddOns/GearHelper/"
    )


if "__main__" == __name__:
    # os.system("cd /Users/Raph/Documents/HE/WebScraping")
    GetClasses()
    GetNoxxicStats()
    CreateWeightValuesFile()
    # CheckDiff()
    # RemoveUnusedFiles()
