#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 08:29:05 2024

@author: atlas
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# import Action chains  
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException

import random

from difflib import SequenceMatcher
import os

# %%Functions definition

#HUMANIZE_MEAN_TIME = 10
#HUMANIZE_RANDRANGE = (-4, 20)

def humanize():
    # better non farsi sgamare
    time.sleep(2.5 + random.uniform(-1,3))


    
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# %% Load company profiles

FOLLOWUP_FILE = "outputs/companies"

FOLLOWUP = []

# load already visited profiles
with open(FOLLOWUP_FILE) as follows_file:
    FOLLOWUP = [line.rstrip() + 'people/' for line in follows_file]
    
# filter companies
FOLLOWUP = list(filter(lambda profile: "company" in profile, FOLLOWUP))


# %% Profile info, credentials and parameters

# profile info and storage
USERNAME = ""
PASSWORD = ""
LANG = "en"
BROWSER = 'firefox'

PROFILES_FILE = "outputs/company_people"
SIMILARITY_THRESHOLD = 0.8


# %% Initialize driver

def switch_driver():
    if BROWSER == 'firefox':
        return webdriver.Firefox()
    elif BROWSER == 'chrome':
        return webdriver.Chrome()

def isBrowserAlive(driver):
   try:
      driver.current_url
      # or driver.title
      return True
   except:
      return False

ALREADY_LOGGED_IN = False

# take existing driver if there is one open
def get_driver():
    try:
        if isBrowserAlive(driver):
            ALREADY_LOGGED_IN = True
            return driver
        else:
            return switch_driver()
    except NameError:
        return switch_driver()
    
    
driver = get_driver()



# %% Language

# define languages
lang = {
        'en' : {
            'connect_button' : 'Connect',
            'follow_button' : 'Follow',
            'message' : 'Message',
            'send_without_note' : "Send without a note",
            'not_now' : "Not now",
            'italy' : 'Italy'
            },
        'it' : {
            'connect_button' : 'Collegati',
            'follow_button' : 'Segui',
            'message' : 'Messaggio',
            'send_without_note' : "Invia senza nota",
            'not_now' : "Non ora",
            'italy' : 'Italia'
            }
    }

# define macros

CONNECT_BUTTON = lang[LANG]['connect_button']
FOLLOW_BUTTON = lang[LANG]['follow_button']
SEND_WITHOUT_NOTE = lang[LANG]['send_without_note']
NOT_NOW = lang[LANG]['not_now']
ITALY = lang[LANG]['italy']
MESSAGE_BUTTON = lang[LANG]['message']


# %% Login

if not ALREADY_LOGGED_IN:

    driver.get("https://linkedin.com")

    humanize()

    username = driver.find_element("xpath", "//input[@name='session_key']")
    password = driver.find_element("xpath", "//input[@name='session_password']")

    username.send_keys(USERNAME)
    password.send_keys(PASSWORD)

    humanize()

    #submit = driver.find_element("xpath", "//button[@name='submit']").click()
    submit = driver.find_element("xpath", "/html/body/main/section[1]/div/div/form/div[2]/button").click()

    humanize()
    
    ALREADY_LOGGED_IN = True
    
    
# %% Match specific keywords in description

RELEVANT_KEYWORDS = {
        'director' : 10,
        'ceo' : 10,
        'dirigente' : 10,
        'delegato' : 10,
        'direttore' : 10,
        'co-founder' : 10,
        'founder' : 10,
        'fondatore' : 10,
        'co-fondatore' : 10,
    }

def relevance_score(description):
    
    # score 
    score = 0
    
    # separe description into keywords
    words = [word.strip().lower() for word in description.split(' ')]
    
    for word in words:
        for key, value in RELEVANT_KEYWORDS.items():
            if similar(word, key) > SIMILARITY_THRESHOLD:
                score += value
    
    return score
    
# %% Start algorithm

def get_profile_li(button):
    
    lis = button.find_elements(By.XPATH, ".//ancestor::li[contains(@class, 'org-people-profile-card__profile-card-spacing')]")
    
    if len(lis) > 0:
        return lis[0]
    else:
        return None
    

def get_profile_link(li):
    
    # recurse down an find <a href=>
    a = li.find_element(By.XPATH, ".//a[@href]")
    miniprofile = a.get_attribute("href")
        
    # get clear link
    return miniprofile.split('?')[0] + '/'



def get_profile_description(li):
    
    divs = li.find_elements(By.XPATH, ".//div[contains(@class, 't-14')]")
    
    if len(divs) > 0:
        return divs[0].text
    else:
        return None
        
            
        
def find_people(maxn = 3):
    
    # get general div
    divs = driver.find_elements(By.XPATH, '//div[contains(@class, "org-people-profile-card__card-spacing")]')
    div = divs[0] if len(divs) > 0 else None
    
    if div is None:
        print("Can't access to people")
        return []
    
    # get child buttons
    all_buttons = div.find_elements(By.TAG_NAME, "button")
    
    # find connect and message button
    message_buttons = [btn for btn in all_buttons if btn.text == MESSAGE_BUTTON and "--secondary" in btn.get_attribute("class")]
    connect_buttons = [btn for btn in all_buttons if btn.text == CONNECT_BUTTON and "--secondary" in btn.get_attribute("class")]
    follow_buttons = [btn for btn in all_buttons if btn.text == FOLLOW_BUTTON and "--secondary" in btn.get_attribute("class")]
    interest_buttons = message_buttons + connect_buttons + follow_buttons
    
    if len(interest_buttons ) > 50:
        return []
    
    people = {}
    
    # get profile links and append if not None
    for button in interest_buttons:
        li = get_profile_li(button)
        
        if li is not None:
            
            # get description
            description = get_profile_description(li)
             
            # get link
            link = get_profile_link(li)
            
            score = relevance_score(description)
            
            if score > 0:
                people[link] = score
            
    links = sorted(people.keys(), key = lambda x: people[x], reverse=True)
    
    return links[:min(len(links), maxn)]


    
# load already collected people
VISITED = []

if os.path.isfile(PROFILES_FILE):

    # load already visited profiles
    with open(PROFILES_FILE) as profiles_file:
        VISITED = [line.rstrip() for line in profiles_file]

PROFILES = []

# execute script
for company in FOLLOWUP:
    
    # get the page
    driver.get(company)
    humanize()
    
    people = []
    
    # retrieve people for the page
    try:
        people = find_people(maxn = 2)
        
        for link in people:
            print("Found person: ", link)
        
    except StaleElementReferenceException:
        print("Connecting action error")
        print("Component staled -> skipping")
    except NoSuchElementException:
        print("Connection action error")
        print("Component not found -> skipping")
    except ElementClickInterceptedException:
        print("Connection action error")
        print("Component is obscured")
        
    # merge lists
    for person in people:
        if person not in VISITED:
            PROFILES.append(person)
            
# %% Output new found people

f = open(PROFILES_FILE, 'a')
# print results
for p in PROFILES:
    print(p)
    f.write(p + '\n')
    
f.close()  
