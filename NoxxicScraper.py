import requests
import time
import os
import difflib
import re
import json
from bs4 import BeautifulSoup

wowClassesUrl = "https://wowwiki.fandom.com/wiki/SpecializationID"
# path = "/Users/Raph/Documents/HE/WebScraping/"
path = ""
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


def CleanPawnString(pawnString) -> str:
    pawnString = pawnString.replace("HasteRating", "Haste")
    pawnString = pawnString.replace("CritRating", "CriticalStrike")
    pawnString = pawnString.replace("MasteryRating", "Mastery")
    pawnString = pawnString.replace("DPS", "MainHandDps")

    return pawnString


def GenerateGHStringFromPawn(pawnDict) -> str:
    # if pawnDict doesn't contains a key named "Intellect"
    ghString = ""
    if pawnDict.get("Intellect"):
        ghString += "Intellect " + str(pawnDict["Intellect"]) + " > "
    if pawnDict.get("Haste"):
        ghString += "Haste " + str(pawnDict["Haste"]) + " > "
    if pawnDict.get("CriticalStrike"):
        ghString += "CriticalStrike " + str(pawnDict["CriticalStrike"]) + " > "
    if pawnDict.get("Versatility"):
        ghString += "Versatility " + str(pawnDict["Versatility"]) + " > "
    if pawnDict.get("Mastery"):
        ghString += "Mastery " + str(pawnDict["Mastery"]) + " > "
    if pawnDict.get("Agility"):
        ghString += "Agility " + str(pawnDict["Agility"]) + " > "
    if pawnDict.get("Stamina"):
        ghString += "Stamina " + str(pawnDict["Stamina"]) + " > "
    if pawnDict.get("Strength"):
        ghString += "Strength " + str(pawnDict["Strength"]) + " > "
    if pawnDict.get("MainHandDps"):
        ghString += "MainHandDps " + str(pawnDict["MainHandDps"]) + " > "
    if pawnDict.get("OffHandDps"):
        ghString += "OffHandDps " + str(pawnDict["OffHandDps"]) + " > "

    return ghString[:-3]


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
                "https://www.noxxic.com/wow/"
                + specName
                + "-"
                + className
                + "/stat-priority/"
            ).lower()

            # print("url : " + str(wowClassesUrl))

            # Try to connect to noxxic link previously created
            response = requests.get(wowClassesUrl)
            if not response.ok:
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            bubbles = soup.findAll("p", {"class": "matrix__bubble"})

            # If stats exists, add them to the file, formated for GH
            bubble = bubbles[1].text

            file.write(
                "    -- "
                + className.upper().replace("-", " ")
                + " "
                + specName.upper().replace("-", " ")
                + " --\n"
            )
            file.write("    [" + str(specID) + "] = {\n")

            if len(bubbles) > 2:  # Si les stats sont présentes
                file.write(
                    '        ["NOX"] = "'
                    + str(bubble)
                    .replace("&gt;", ">")
                    .replace("(", "[")
                    .replace(")", "]")
                    + '"\n'
                )
            else:  # Sinon on parse la pawn string
                # Parse pawn string
                # {Class:Priest, Spec:Holy, Intellect:7.52, HasteRating:6.11, CritRating:5.72, Versatility:5.72, MasteryRating:5.11}

                # replace char at index 10 from bubble by ","
                bubble = bubble[:10] + "," + bubble[11:]
                bubble = bubble.replace("=", ":")

                # Format bubble string to a dict compatible
                bubble = re.sub(r", \".+: ", ",", bubble)
                bubble = re.sub(r"(\w+):", r'"\1":', bubble)
                bubble = re.sub(r"([A-z]+),", r'"\1",', bubble)
                bubble = '{"' + bubble[bubble.find("C") : -1] + "}"

                bubble = CleanPawnString(bubble)

                # string to dict
                bubble = json.loads(bubble)

                ghString = GenerateGHStringFromPawn(bubble)

                file.write('        ["NOX"] = "' + ghString + '"\n')

            file.write("    },\n")

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
    with open(str(path) + "StatsActuelles.txt", "w") as outfile:
        for fname in filenames:
            with open(fname) as infile:
                outfile.write(infile.read())

    # Remove file part2 (the one created with noxxic values)
    os.remove(str(path) + "part2.txt")

    with open(str(path) + "StatsActuelles.txt") as f1:
        f1_text = f1.read()
    with open(
        "/Applications/World of Warcraft/_retail_/Interface/AddOns/GearHelper/WeightValues.lua"
    ) as f2:
        f2_text = f2.read()


def CheckDiff() -> bool:
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
        "cp " + str(path) + "StatsActuelles.txt " + str(path) + "WeightValues.lua"
    )
    os.remove(str(path) + "StatsActuelles.txt")


if "__main__" == __name__:
    GetClasses()
    GetNoxxicStats()
    CreateWeightValuesFile()
    CheckDiff()
    RemoveUnusedFiles()