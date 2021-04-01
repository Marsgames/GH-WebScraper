# https://www.codeur.com/users/406501/messages/archived?page=1

# import requests
import time
import re

from selenium import webdriver
from bs4 import BeautifulSoup

browser = webdriver.Chrome()

codeurLogin = "https://www.codeur.com/users/sign_in"
codeurMessages = "https://www.codeur.com/users/406501/messages/archived?page="


def login():
    browser.get(codeurLogin)
    loginURL = browser.current_url

    # Set username + password
    browser.find_element_by_id("user_email").send_keys("admin@headcrab.fr")
    browser.find_element_by_id("user_password").send_keys("vypbu7-woqvur-zytqYd")

    # Check if cookie banner is displayed + close it
    cookie = browser.find_element_by_class_name("accept-cookies-btn")
    if cookie.is_displayed() and cookie.is_enabled():
        cookie.click()

    # submit login infos
    browser.find_element_by_name("commit").click()

    # Wait for user to solve captcha
    while browser.current_url == loginURL:
        time.sleep(1)


def getAllMessages():
    browser.get(codeurMessages)

    # get last page
    hrefString = browser.find_elements_by_class_name("page-link")[-1].get_attribute(
        "href"
    )
    hrefString = re.sub("^.*=", "", hrefString)
    index = int(hrefString)

    # Foreach page, get all urls
    messagesLink = []
    while index > 0:
        print(f"url : {codeurMessages}{index}")
        browser.get(codeurMessages + str(index))
        response = browser.page_source
        index -= 1
        soup = BeautifulSoup(response, "html.parser")
        for elem in soup.find_all("div", {"class": "offer-link"}):
            messagesLink.append(elem["data-url"])
        time.sleep(1)
    return messagesLink


# Get text from page
def ExtractPageContent(link) -> str:
    text = ""
    try:
        browser.get(f"https://www.codeur.com{link}")
        response = browser.page_source

        soup = BeautifulSoup(response, "html.parser")
        text += f"========== {soup.title.text} =========="
        for elem in soup.find_all("div", {"class": "comment-content"}):
            text += "\n---\n"
            text += str(elem.text)
        text += "\n---------- ---------- ----------\n\n"
    except AttributeError:
        print(f"page (https://www.codeur.com{link}) cannot be processed")

    return text


def getMessagesContent(messagesLink):
    textsArray = []
    index = 0
    for link in messagesLink:
        print(f"Restant : {len(messagesLink) - index}")
        text = ExtractPageContent(link)

        if not text:
            time.sleep(60)
            text = ExtractPageContent(link)

        textsArray.append(text)
        index += 1

    return textsArray


def writeFile(text):
    with open("AllMessages.txt", "a") as file:
        for elem in text:
            file.write(elem)


if "__main__" == __name__:
    login()
    messages = getAllMessages()
    allMessages = getMessagesContent(messages)
    writeFile(allMessages)