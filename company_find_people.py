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

#from difflib import SequenceMatcher
import os
from thefuzz import fuzz

# %%Functions definition

def humanize():
    # better non farsi sgamare
    time.sleep(2.5 + random.uniform(-1,3))


def similar(shorter, longer):
    return fuzz.partial_ratio(shorter, longer) / 100.0

# %% Load company profiles

FOLLOWUP_FILE = "outputs/companies"

FOLLOWUP = []

# load already visited profiles
with open(FOLLOWUP_FILE) as follows_file:
    FOLLOWUP = [line.rstrip() + 'people/' for line in follows_file]
    
# filter companies
FOLLOWUP = list(filter(lambda profile: "company" in profile, FOLLOWUP))

# %% Load visited companies

VISITED_FILE = "outputs/visited_companies"

VISITED_COMPANIES = []

# load already visited profiles
with open(VISITED_FILE) as follows_file:
    VISITED_COMPANIES = [line.rstrip() + 'people/' for line in follows_file]
    
# filter companies
VISITED_COMPANIES = list(filter(lambda profile: "company" in profile, VISITED_COMPANIES))

# %% Filter already done

# remove visited from followup
FOLLOWUP = set(FOLLOWUP).difference(set(VISITED_COMPANIES))

# %% Profile info, credentials and parameters

# profile info and storage
USERNAME = ""
PASSWORD = ""
LANG = "it"
BROWSER = 'firefox'

PROFILES_FILE = "outputs/company_people"
SIMILARITY_THRESHOLD = 0.9


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
        'amministratore delegato' : 10,
        'direttore generale' : 10,
        'direttore operativo' : 5,
        'co-founder' : 10,
        'founder' : 10,
        'fondatore' : 10,
        'co-fondatore' : 10,
    }

def relevance_score(description):
    
    # score 
    score = 0
    
    # separe description into keywords
    #words = [word.strip().lower() for word in description.split(' ')]
    
    #for word in words:
    #    for key, value in RELEVANT_KEYWORDS.items():
    #        if similar(word, key) > SIMILARITY_THRESHOLD:
    #            score += value
    
    for key, value in RELEVANT_KEYWORDS.items():
        # take the exact match
        if similar(key, description.lower()) > SIMILARITY_THRESHOLD:
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
            
            if description is None:
                continue
             
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

f = open(PROFILES_FILE, 'a')
company_f = open(VISITED_FILE, 'a')

# execute script
for company in FOLLOWUP:
    
    # get the page
    driver.get(company)
    humanize()
    
    people = []
    
    # retrieve people for the page
    try:
        people = find_people(maxn = 1)
        
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
            f.write(person + '\n')
            
    # everything good so mark as visited company
    VISITED_COMPANIES.append(company)
    company_f.write(company + '\n')
            
f.close() 
company_f.close()

# %% Output new found people

# print results
for p in PROFILES:
    print(p)

    
 
