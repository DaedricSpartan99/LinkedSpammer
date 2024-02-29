#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 21:48:08 2024

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
    
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# %% Initialize driver

driver = webdriver.Firefox()

ALREADY_LOGGED_IN = False

# %% Profile info, credentials and parameters

# profile info and storage
USERNAME = ""
PASSWORD = ""
FOLLOWUP_FILE = "Followup"
LANG = "en"

#USERNAME = "desky.lausanne@gmail.com"
#PASSWORD = "Fabio@nobile2024"
#FOLLOWUP_FILE = "Followup_desky"
#LANG = "it"


# algorithm parameters
SIMILARITY_THRESHOLD = 0.8
STOP_AT = 50
SEED ="https://www.linkedin.com/company/ferrovie-dello-stato-s-p-a/"


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
    

# %% Implement language difference

# define languages
lang = {
        'en' : {
            'connect_button' : 'Connect',
            'follow_button' : 'Follow',
            'send_without_note' : "Send without a note",
            'not_now' : "Not now",
            'italy' : 'Italy'
            },
        'it' : {
            'connect_button' : 'Collegati',
            'follow_button' : 'Segui',
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

# %% Get italian geographical data

# load database
df = pd.read_excel('./Elenco-comuni-italiani.xls')

# filter to interested columns
regions = list(df['Denominazione Regione'].unique())

provincia = list(df["Denominazione dell'Unità territoriale sovracomunale \n(valida a fini statistici)"].unique())

cities = list(df['Denominazione in italiano'].dropna())

# %% Load visited profiles

VISITED = []

# load already visited profiles
with open(FOLLOWUP_FILE) as follows_file:
    VISITED = follows_file.readlines()

# %% Connect to profiles


PROFILES = []

def find_and_press_connect_button(profile):
    
    # track state
    success = False
    
    # get connect button 
    all_buttons = driver.find_elements(By.TAG_NAME, "button")
    
    connect_buttons = [btn for btn in all_buttons if btn.text == CONNECT_BUTTON and "--primary" in btn.get_attribute("class")]
    follow_primary_buttons = [btn for btn in all_buttons if btn.text == FOLLOW_BUTTON and "--primary" in btn.get_attribute("class")]
    follow_secondary_buttons = [btn for btn in all_buttons if btn.text == FOLLOW_BUTTON and "--secondary" in btn.get_attribute("class")]
    
    # person with connect button showing up
    if len(connect_buttons) > 0:
        print("Found connect button: ", connect_buttons[0].get_attribute("id"))
        connect_buttons[0].click()
        success = True
        PROFILES.append(profile)
        humanize()
        
        # restore page
        buttons = driver.find_elements(By.TAG_NAME, "button")
        no_note = [btn for btn in buttons if btn.text == SEND_WITHOUT_NOTE]
        if len(no_note) > 0:
            no_note[0].click()
            humanize()
        
        buttons = driver.find_elements(By.TAG_NAME, "button")
        not_now = [btn for btn in buttons if btn.text == NOT_NOW]
        if len(not_now) > 0:
            not_now[0].click()
            humanize()
            
    else:
        
        # primary = company
        # secondary = person
        follow_buttons = follow_primary_buttons if len(follow_primary_buttons) > 0 else follow_secondary_buttons

        if len(follow_buttons) < 0:
            # unsuccess
            print("Couldn't find a follow button")
            return False
        
        print("Found follow button: ", follow_buttons[0].get_attribute("id"))
            
        follow_buttons[0].click()
        
        success = True
        PROFILES.append(profile)
        humanize()
            
        # restore page
        buttons = driver.find_elements(By.TAG_NAME, "button")
        not_now = [btn for btn in buttons if btn.text == NOT_NOW]
        if len(not_now) > 0:
            not_now[0].click()
            humanize()
    
    return success
            

def collect_links_connect(all_buttons):
    
    candidates = []
    spread_buttons = [btn for btn in all_buttons if btn.text == CONNECT_BUTTON and "--secondary" in btn.get_attribute("class")]
    
    for button in spread_buttons:
        # get profile name
        #label = button.get_attribute("aria-label")
        #regex = re.compile(r"Invita (.*) a collegarsi")
        #name = regex.search(label).group(1)
        #print("Spread name: ", name)
        # search other profile link
        divs_people = button.find_elements(By.XPATH, './/ancestor::div[@data-view-name="profile-component-entity"]')
        
        
        if len(divs_people) > 0:
            print("Collect: People found")
            div = divs_people[0]
        
        if div is not None:
            a = div.find_element(By.XPATH, './/a[@href]')
            link = a.get_attribute("href")
        
            # if everything is fine recurse
            if link not in VISITED:
                print("Possible spread link: ", link)
                candidates.append(link)
                VISITED.append(link)
                
    return candidates

def collect_links_follow(all_buttons):
    
    spread_follow_buttons = [btn for btn in all_buttons if btn.text == FOLLOW_BUTTON and "--secondary" in btn.get_attribute("class")]
    
    candidates = []
    
    # follow all profiles            
    for button in spread_follow_buttons:
        # get profile name
        #label = button.get_attribute("aria-label")
        #regex = re.compile(r"Segui (.*)")
        #name = regex.search(label).group(1)
        #print("Spread name: ", name)
        
        # search other profile link
        divs_people = button.find_elements(By.XPATH, './/ancestor::div[@data-view-name="profile-component-entity"]')
        divs_company = button.find_elements(By.XPATH, './/ancestor::div[contains(@class, "org-view-entity-card__container")]')
        div = None
        
        if len(divs_people) > 0:
            print("Collect: People found")
            div = divs_people[0]
        elif len(divs_company) > 0:
            print("Collect: Company found")
            div = divs_company[0]
        
        if div is not None:
            a = div.find_element(By.XPATH, './/a[@href]')
            link = a.get_attribute("href")
        
            # if everything is fine recurse
            if link not in VISITED:
                print("Possible spread link: ", link)
                candidates.append(link)
                VISITED.append(link)
                
    return candidates


def is_italian(profile):
    
    print("Examine profile: ", profile)
    driver.get(profile)
    humanize()
    
    # detect profile description
    target_divs = driver.find_elements(By.XPATH, '//div[@class="ph5 pb5"]')
    target_div = None
    
    if len(target_divs) > 0:
        target_div = target_divs[0]
    else:
        print("Italian check: couldn't find profile description")
        return False
    
    # ispect nationality
    spans = target_div.find_elements(By.XPATH, ".//span[contains(text(),'%s')]" % ITALY)
    
    print("Checking keyword Italia as provenance")
    
    if len(spans) > 0:
        # connect condition satisfied
        print("Italian person found")
        return True
        
    # maybe its a company
    # target specifically the second
    blocks = target_div.find_elements(By.XPATH, './/div[@class="inline-block"]')
    text_div = None
    
    if len(blocks) > 0:
        text_divs = blocks[0].find_elements(By.CLASS_NAME, "org-top-card-summary-info-list__info-item")
        text_div = text_divs[0] if len(text_divs) > 0 else None
    
    # get text and verify keywords
    text = text_div.text
    print("Checking text: ", text)
    wordlist = text.split(',')
    wordlist = [word.strip() for word in wordlist]
    
    print("Found word list: ", wordlist)
    
    # check geography location
    for word in wordlist:
        decap = word.lower()
        
        print("Checking regions")
        
        # check regions
        for r in regions:
            score = similar(decap, r.lower())
            if score > SIMILARITY_THRESHOLD:
                # match
                print("Match regions found with score: ", score)
                return True
            
        print("Checking province")
        
        # check provincia
        for r in provincia:
            score = similar(decap, r.lower())
            if score > SIMILARITY_THRESHOLD:
                # match
                print("Match provincia found with score: ", score)
                return True
            
        print("Checking cities")
                
        # check cities
        for r in cities:
            score = similar(decap, r.lower())
            if score > SIMILARITY_THRESHOLD:
                # match
                print("Match cities found with score: ", score)
                return True
    
    return False

    

def connect(profile):
    
    if len(PROFILES) >= STOP_AT:
        return

    # get the page
    driver.get(profile)
    humanize()

    # phase 1: connect or follow
    try:
        # 
        if not find_and_press_connect_button(profile):
            print("Unsuccessful connection on profile: ", profile )
        
    except StaleElementReferenceException:
        print("Connecting action error")
        print("Component staled -> skipping")
    except NoSuchElementException:
        print("Connection action error")
        print("Component not found -> skipping")
    except ElementClickInterceptedException:
        print("Connection action error")
        print("Component is obscured")
        
        
    
    candidates = []
    
    # phase 2: look for other candidates
    try:
            
        # look for other contacts
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        
        # collect all profiles
        candidates = collect_links_connect(all_buttons) + collect_links_follow(all_buttons)
        
    except StaleElementReferenceException:
        print("Profile retrieval error")
        print("Component staled -> skipping")
        return
    except NoSuchElementException:
        print("Profile retrieval error")
        print("Component not found -> skipping")
        return

    print("Found %d candidates" % len(candidates))
    
    italian_candidates = []
    
    try:              
        # inspect profiles
        italian_candidates = filter(lambda link: is_italian(link), candidates)              
                
    except StaleElementReferenceException:
        print("Link inspection error")
        print("Component staled -> skipping")
        return
    except NoSuchElementException:
        print("Link inspection error")
        print("Component not found -> skipping")
        return
    
    #print("Adding %d italian candidates" % len(list(italian_candidates)))
    
    # finally recurse into filtered candidates
    for link in italian_candidates:
        connect(link)
        

# Execute with a seed
connect(SEED)

# %% Store profiles
f = open(FOLLOWUP_FILE, 'a')
# print results
for p in PROFILES:
    print(p)
    f.write(p + '\n')
    
f.close()  
    

   
