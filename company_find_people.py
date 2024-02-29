#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 08:29:05 2024

@author: atlas
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time

# import Action chains  
from selenium.webdriver.common.action_chains import ActionChains 
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException

import re
import random

import pandas as pd
from difflib import SequenceMatcher

# %%Functions definition

#HUMANIZE_MEAN_TIME = 10
#HUMANIZE_RANDRANGE = (-4, 20)

def humanize():
    # better non farsi sgamare
    time.sleep(2.5 + random.uniform(-1,3))


# %% Load company profiles

FOLLOWUP_FILE = "Followup"

FOLLOWUP = []

# load already visited profiles
with open(FOLLOWUP_FILE) as follows_file:
    FOLLOWUP = [line.rstrip() + 'people/' for line in follows_file]
    
# filter companies
FOLLOWUP = list(filter(lambda profile: "company" in profile, FOLLOWUP))

# %% Initialize driver

driver = webdriver.Firefox()

ALREADY_LOGGED_IN = False

# %% Profile info, credentials and parameters

# profile info and storage
USERNAME = ""
PASSWORD = ""
LANG = "en"

PROFILES_FILE = "People"

#USERNAME = "desky.lausanne@gmail.com"
#PASSWORD = "Fabio@nobile2024"
#FOLLOWUP_FILE = "Followup_desky"
#LANG = "it"

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
    
# %% Start algorithm

def get_profile_link(button):
    
    lis = button.find_elements(By.XPATH, ".//ancestor::li[contains(@class, 'org-people-profile-card__profile-card-spacing')]")
    
    if len(lis) > 0:
        li = lis[0]
        
        # recurse down an find <a href=>
        a = li.find_element(By.XPATH, ".//a[@href]")
        miniprofile = a.get_attribute("href")
        
        # get clear link
        return miniprofile.split('?')[0] + '/'

    return None
            
        
def find_people():
    
    # get general div
    divs = driver.find_elements(By.XPATH, '//div[contains(@class, "org-people-profile-card__card-spacing")]')
    div = divs[0] if len(divs) > 0 else None
    
    # get child buttons
    all_buttons = div.find_elements(By.TAG_NAME, "button")
    
    # find connect and message button
    message_buttons = [btn for btn in all_buttons if btn.text == MESSAGE_BUTTON and "--secondary" in btn.get_attribute("class")]
    connect_buttons = [btn for btn in all_buttons if btn.text == CONNECT_BUTTON and "--secondary" in btn.get_attribute("class")]
    interest_buttons = message_buttons + connect_buttons
    
    people = []
    
    # get profile links and append if not None
    for button in interest_buttons:
        link = get_profile_link(button)
        if link is not None:
            print("Found person: ", link)
            people.append(link)
    
    return people


    
# load already collected people
VISITED = []

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
        people = find_people()
        
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
