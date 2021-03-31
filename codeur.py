# https://www.codeur.com/users/406501/messages/archived?page=1

# import requests
import os
import time
from selenium import webdriver
from bs4 import BeautifulSoup

browser = webdriver.Chrome()

codeurLogin = "https://www.codeur.com/users/sign_in"
codeurMessages = "https://www.codeur.com/users/406501/messages/archived?page="
lastIndex = 15


def login():
    browser.get(codeurLogin)
    browser.find_element_by_id("user_email").send_keys("admin@headcrab.fr")
    browser.find_element_by_id("user_password").send_keys("vypbu7-woqvur-zytqYd")
    os.system('read -s -n 1 -p "Press any key to continue..."')
    print()
    browser.find_element_by_name("commit").click()
    os.system('read -s -n 1 -p "Press any key to continue..."')
    print()


def getAllMessages(index):
    messagesLink = []
    while index > 0:
        print("url : " + str(codeurMessages + str(index)))
        browser.get(codeurMessages + str(index))
        response = browser.page_source
        index -= 1
        soup = BeautifulSoup(response, "html.parser")
        for elem in soup.find_all("div", {"class": "offer-link"}):
            messagesLink.append(elem["data-url"])
        time.sleep(1)
    return messagesLink


def getMessagesContent(messagesLink):
    textsArray = []
    index = 0
    for link in messagesLink:
        text = ""
        index += 1
        print("Restant : " + str(len(messagesLink) - index))
        print("https://www.codeur.com" + link)
        browser.get("https://www.codeur.com" + link)
        response = browser.page_source
        # with open("oneMessage.txt", "r") as file:
        #     response = file.read()

        soup = BeautifulSoup(response, "html.parser")
        text += "========== " + str(soup.title.text) + " =========="
        for elem in soup.find_all("div", {"class": "comment-content"}):
            text += "\n---\n"
            text += str(elem.text)
        text += "\n---------- ---------- ----------\n\n"
        textsArray.append(text)
    return textsArray


def writeFile(text):
    with open("AllMessages.txt", "a") as file:
        for elem in text:
            file.write(elem)


login()
messages = getAllMessages(lastIndex)
# print(messages)
allMessages = getMessagesContent(messages)
writeFile(allMessages)

# with open("archive.txt", "r") as file:
#         response = file.read()

# while lastIndex > 14:
#     response = requests.get(codeurMessages + str(lastIndex))
#     print(codeurMessages + str(lastIndex))
#     lastIndex -= 1
# if not response.ok:
#     print("No response. Quit")
#     exit()

#     soup = BeautifulSoup(response.text, "html.parser")
#     print(response.text)
#     messages = soup.find("closed")

#     print(messages)
