import requests
import time
import os
import difflib

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

wowClassesUrl = "https://wowwiki.fandom.com/wiki/SpecializationID"
# path = "/Users/Raph/Documents/HE/WebScraping/"
path = ""

response = requests.get(wowClassesUrl)
if (not response.ok):
    exit()

linksDic = {}
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
    if (not line[0].isdigit()):
        classNames = line
    else:
        id = line.split("-")[0]
        spec = line.split("-")[-1]
        linksDic[id] = (classNames, spec)

# Create a file named "part2" wich will contain noxxic stats
with open(str(path) + "part2.txt", "w") as file:
    # Foreach spec, create a noxxic link
    for item in linksDic.items():
        className = item[1][0]
        specName = item[1][1]
        specID = str(item[0])
        wowClassesUrl = (
            "https://www.askmrrobot.com/optimizer#" + className.replace("-", "") + specName).lower()

        # print("url : " + str(wowClassesUrl))

        # Try to connect to noxxic link previously created
        # response = requests.get(wowClassesUrl)
        # if (not response.ok):
        #     continue

        browser = webdriver.Safari()
        browser.get(wowClassesUrl)

        try:
            buttons = browser.find_element_by_id(
                "dlgHelp").find_elements_by_class_name("c-button-flat")

            for button in buttons:
                if (button.text == "Close"):
                    button.click()
        except NoSuchElementException:
            print("hop hop pas de chance")
            browser.close()
            exit()

        gearCheck = browser.find_elements_by_id("cmdExpOptimize")
        for button in gearCheck:
            if (button.text == "Do a Gear Check"):
                button.click()

        time.sleep(3)

        stats = browser.find_elements_by_class_name("wc-stat-item")

        for stat in stats:
            print(stat.find_element_by_class_name("name").text +
                  " - " + stat.find_element_by_class_name("gear").text)

#         soup = BeautifulSoup(response.text, "html.parser")
#         bubbles = soup.findAll("p", {"class": "matrix__bubble"})

#         # If stats exists, add them to the file, formated for GH
#         if (len(bubbles) > 2):
#             bubble = bubbles[1]
#             file.write("    -- " + className.upper().replace("-", " ") +
#                        " " + specName.upper().replace("-", " ") + " --\n")
#             file.write("    [" + str(specID) + "] = {\n")
#             file.write("        [\"NOX\"] = \"" +
#                        str(bubble.text).replace("&gt;", ">").replace("(", "[").replace(")", "]") + "\"\n")
#             file.write("    },\n")
#         else:  # If stats doesn't exist, add empty string
#             file.write("    -- " + className.upper().replace("-", " ") +
#                        " " + specName.upper().replace("-", " ") + " --\n")  # We should parse pawn string
#             file.write("    [" + str(specID) + "] = {\n")
#             file.write("        [\"NOX\"] = \"\"\n")
#             file.write("    },\n")

#     time.sleep(1)

# # Concatenate files part1, part2 and part3
# filenames = [
#     str(path) + 'part1.txt', str(path) + 'part2.txt', str(path) + 'part3.txt']
# with open(str(path) + 'StatsActuelles.txt', 'w') as outfile:
#     for fname in filenames:
#         with open(fname) as infile:
#             outfile.write(infile.read())

# # Remove file part2 (the one created with noxxic values)
# os.remove(str(path) + "part2.txt")

# with open(str(path) + 'StatsActuelles.txt') as f1:
#     f1_text = f1.read()
# with open('/Applications/World of Warcraft/_retail_/Interface/AddOns/GearHelper/WeightValues.lua') as f2:
#     f2_text = f2.read()

# # The notifier function
# def notify(title, message):
#     # This requires a mac + terminal-notifier + the right path
#     # Do not call this function if you do not need it
#     os.system('terminal-notifier -title "' + title + '" -message "' + message +
#               '" -activate com.apple.Terminal -execute "wdiff /Applications/World\ of\ Warcraft/_retail_/Interface/AddOns/GearHelper/WeightValues.lua /Users/Raph/Documents/GH/statsAJour.txt | colordiff" -appIcon "https://media.forgecdn.net/avatars/thumbnails/54/445/64/64/636135209663914354.png"')

# # Find differences
# diffs = 0
# for line in difflib.unified_diff(f1_text, f2_text, fromfile='file1', tofile='file2', lineterm=''):
#     diffs += 1

# # Show notification if any diff
# if (diffs > 0):
#     # Calling the function
#     notify(title='GearHelper',
#            message='Les stats Noxxic ont changées !!')

# # Remove unused files
# os.system(
#     "cp " + str(path) + "StatsActuelles.txt " + str(path) + "WeightValues.lua")
# os.remove(str(path) + "StatsActuelles.txt")
