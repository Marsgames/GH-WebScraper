import requests
import sys
import time
import os
from bs4 import BeautifulSoup
from selenium import webdriver
import getpass
import argparse


parser = argparse.ArgumentParser(description="Login to worldofwarcraft.com")
parser.add_argument('--quiet', default=False, action='store_true')
parser.add_argument('--login', metavar='login')
parser.add_argument('--password', metavar='pass')

args = parser.parse_args()
if not args.password or not arg.login:
    exit()

# Use Chroma, there is a bug with Firefox for upload file
browser = webdriver.Safari()
# Login
browser.get("https://worldofwarcraft.com/fr-fr/login")
# getpass.getpass("Press Enter after You are done logging in")

username = browser.find_element_by_id('accountName')
username.send_keys(args.login)
password = browser.find_element_by_id('password')
password.send_keys(args.password)
browser.find_element_by_id("submit").click()

getpass.getpass("Press enter when you have accept authentication request")

# Redirect on the achievements page after login
browser.get("https://account.blizzard.com")
# Get all the achievements
# panels = browser.find_elements_by_class_name("panel-body")
# achievements = []
# print(len(panels))
# for p in panels:
#     try:
#         row = p.find_element_by_class_name("row")
#         try:
#             if(row.find_element_by_class_name("input-group-addon").text == "API Key"):
#                 achievements.append(row)
#         except:
#             pass
#     except:
#         pass
# print(len(achievements))
# # Upload icons for each achievement
# i = 0
# for achiev in achievements:
#     title = achiev.find_element_by_id(
#         'achievement_collection_achievements_'+str(i)+'_key').get_attribute("value")
#     achiev.find_element_by_id('achievement_collection_achievements_'+str(
#         i)+'_fileUploadUnlocked').send_keys("F:/Projects/deadcells/tps/achievements/64x64/"+title+".jpg")
#     achiev.find_element_by_id('achievement_collection_achievements_'+str(
#         i)+'_fileUploadLocked').send_keys("F:/Projects/deadcells/tps/achievements/64x64/"+title+"Off.jpg")
#     i += 1
# browser.find_element_by_class_name("save-all").click()
