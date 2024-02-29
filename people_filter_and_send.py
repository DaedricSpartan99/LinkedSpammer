#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 22:40:59 2024

@author: atlas
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException

# import Action chains  
from selenium.webdriver.common.action_chains import ActionChains 
import random
import pandas as pd
from difflib import SequenceMatcher

# %%Functions preparation


def humanize():
    # better non farsi sgamare
    time.sleep(2.5 + random.uniform(-1,3))
    
    
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# %% Open tab

driver = webdriver.Firefox()
ALREADY_LOGGED_IN = False

# %% INFO + Parameters

USERNAME = ""
PASSWORD = ""
SIMILARITY_THRESHOLD = 0.8

LANG = 'en'

PROFILES_FILE = "People"
SENT_FILE = "Sent"

# %% Login

if not ALREADY_LOGGED_IN:

    driver.get("https://linkedin.com")

    humanize()

    username = driver.find_element("xpath", "//input[@name='session_key']")
    password = driver.find_element("xpath", "//input[@name='session_password']")

    username.send_keys(USERNAME)
    password.send_keys(PASSWORD)

    humanize()

    submit = driver.find_element("xpath", "/html/body/main/section[1]/div/div/form/div[2]/button").click()

    humanize()
    

# %% Language

# define languages
lang = {
        'en' : {
            'connect_button' : 'Connect',
            'follow_button' : 'Follow',
            'message' : 'Message',
            'send_without_note' : "Send without a note",
            'not_now' : "Not now",
            'italy' : 'Italy',
            'premium_message' : 'Get Hired with Premium'
            },
        'it' : {
            'connect_button' : 'Collegati',
            'follow_button' : 'Segui',
            'message' : 'Messaggio',
            'send_without_note' : "Invia senza nota",
            'not_now' : "Non ora",
            'italy' : 'Italia',
            'premium_message' : 'Get Hired with Premium'
            }
    }

# define macros

CONNECT_BUTTON = lang[LANG]['connect_button']
FOLLOW_BUTTON = lang[LANG]['follow_button']
SEND_WITHOUT_NOTE = lang[LANG]['send_without_note']
NOT_NOW = lang[LANG]['not_now']
ITALY = lang[LANG]['italy']
MESSAGE_BUTTON = lang[LANG]['message']
PREMIUM_MESSAGE = lang[LANG]['premium_message']
    
# %% Geographic information

# load database
df = pd.read_excel('./Elenco-comuni-italiani.xls')

# filter to interested columns
regions = list(df['Denominazione Regione'].unique())

provincia = list(df["Denominazione dell'Unità territoriale sovracomunale \n(valida a fini statistici)"].unique())

cities = list(df['Denominazione in italiano'].dropna())

def is_italian():
    
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

# %% Match specific keywords in description

RELEVANT_KEYWORDS = [
        'director',
        'ceo',
        'dirigente',
        'manager',
        'coordinatore',
        'responsabile',
        'gestore',
        'quadro',
        'leader',
        'co-founder',
        'founder',
        'fondatore',
        'co-fondatore',
        'direttore'
    ]

def is_relevant():
    
    target_divs = driver.find_elements(By.XPATH, '//div[@class="ph5 pb5"]')
    target_div = None
    
    if len(target_divs) > 0:
        target_div = target_divs[0]
    else:
        print("Relevant check: couldn't find profile description")
        return False
    
    targets = target_div.find_elements(By.XPATH, ".//div[contains(@class, 'break-words')]")
    description = None
    
    if len(targets) > 0:
        description = targets[0].text
    else:
        print("Relevant check: couldn't find profile description in child div")
        return False
    
    # separe description into keywords
    words = [word.strip().lower() for word in description.split(' ')]
    
    for word in words:
        for r in RELEVANT_KEYWORDS:
            if similar(word, r) > SIMILARITY_THRESHOLD:
                return True
    
    return False

# %% Load people to contact

PROFILES = []

# load  visited profiles
with open(PROFILES_FILE) as f:
    PROFILES = [line.rstrip() for line in f]

# remove duplicates
PROFILES = list(set(PROFILES))

# %% Send message

SENT = []

# load already visited profiles
with open(SENT_FILE) as f:
    SENT = [line.rstrip() for line in f]

# start sending
for profile in PROFILES:
    
    # skip if already sent
    if profile in SENT:
        continue
    
    # get the page
    driver.get(profile)
    humanize()
    
    # check provenance information
    
    # check if relevant
    if not is_relevant():
        print("Not enough relevant profile")
        continue
    
    # get the Message button and click it
    all_buttons = driver.find_elements(By.TAG_NAME, "button")
    
    message_buttons = [btn for btn in all_buttons if btn.text == MESSAGE_BUTTON and "--primary" in btn.get_attribute("class")]

    # click message button
    message_buttons[0].click()
    humanize()
    
    # profile  message limit expired check
    try:
        # search a button
        premium_message = driver.find_elements(By.XPATH, "//div[contains(text(), '%s')]" % PREMIUM_MESSAGE)
        
        if len(premium_message) > 0:
            print("Limit reached per account, stopping simulation")
            break
        
        # submit
        submit = driver.find_element(By.XPATH, "//button[@type='submit']")
        
        # paste command
        action = ActionChains(driver)
        action.key_down(Keys.CONTROL)
        action.send_keys("v")
        action.key_up(Keys.CONTROL)
        action.perform()

        humanize()
        
        # click on submit
        submit.click()
        SENT.append(profile)
        humanize()
        
    except StaleElementReferenceException:
        print("Connecting action error")
        print("Component staled -> skipping")
    except NoSuchElementException:
        print("Connection action error")
        print("Component not found -> skipping")
    except ElementClickInterceptedException:
        print("Connection action error")
        print("Component is obscured")
    
    
# %% Store sent

f = open(SENT_FILE, 'a')
# print results
for p in SENT:
    print(p)
    f.write(p + '\n')
    
f.close()  
   
