#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 21:48:08 2024

@author: atlas
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# import Action chains  
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains 

import random
import os

import pandas as pd
from difflib import SequenceMatcher
import re
import traceback

# %%Functions definition

#HUMANIZE_MEAN_TIME = 10
#HUMANIZE_RANDRANGE = (-4, 20)

def humanize():
    # better non farsi sgamare
    time.sleep(2.5 + random.uniform(-1,3))
    
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


# %% Profile info, credentials and parameters

# profile info and storage
USERNAME = ""
PASSWORD = ""
FOLLOWUP_FILE = "outputs/companies"
LANG = "it"
BROWSER = 'firefox'


# algorithm parameters
SIMILARITY_THRESHOLD = 0.9
MAX_EMPLOYEE = 70
STOP_AT = 200
SEED ="https://www.linkedin.com/company/matdesignitaly/"


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

# blacklist some dangerous words
cities.remove('Floridia')

# %% Load visited profiles

VISITED = []

if os.path.isfile(FOLLOWUP_FILE):

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

        if len(follow_buttons) == 0:
            # unsuccess
            print("Couldn't find a follow button")
            return False
        
        print("Found follow button: ", follow_buttons[0].get_attribute("id"))
            
        follow_buttons[0].click()
        
        success = True
        
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

def close_messages():
    div = driver.find_element(By.XPATH, "//div[contains(@class, 'msg-overlay-bubble-header__controls')]")
    messenger_buttons = div.find_elements(By.XPATH, "//button[contains(@class, 'msg-overlay-bubble-header__control')]")
    
    if len(messenger_buttons) >= 2:
        print("Found messenger close button")
        close_button = messenger_buttons[1]
        close_button.click()
        humanize()
        
def key_down():
    action = ActionChains(driver)
    action.send_keys(Keys.DOWN)
    action.perform()
    humanize()

def find_more_results():
    
    # facilitate the view
    key_down()
    key_down()
    
    # look for other contacts
    sections = driver.find_elements(By.XPATH, "//section[@class='artdeco-card']")
    target = None
        
    # select the correct artdeco
    for section in sections:
        
        elems = section.find_elements(By.XPATH, "//*[contains(text(), 'Altre pagine consultate')]")
        
        if len(elems) > 0:
            target = section
            print("More results: Target found")
            break
        
    if target is None:
        return []
    
    try:
      
        # look for the one with text
        all_buttons = target.find_elements(By.TAG_NAME, "button")
        more_buttons = [btn for btn in all_buttons if btn.text == 'Mostra tutto' ]
        
        print("More results: button found")
        print("Quantity: ", len(more_buttons))
        if len(more_buttons) > 0:
            more_buttons[0].click()
        else:
            return []
        humanize()
        
        div = driver.find_element(By.XPATH, "/div[contains(@class, 'artdeco-modal__content')]")
        print("More results: found div")   
        
        return div.find_elements(By.TAG_NAME, "button")
        
    except NoSuchElementException:
        print("Error finding more results")
        print("Component not found -> skipping")
        return []
    except ElementClickInterceptedException:
        print("Connection action error")
        print("Component is obscured")
        return []
    
    return []

def is_matching(profile):
    
    print("Examine profile: ", profile)
    driver.get(profile)
    humanize()
    
    try:
        return is_italian() and is_small()
    
    except StaleElementReferenceException:
        print("Link inspection error")
        print("Component staled -> skipping")
        return False
    except NoSuchElementException:
        print("Link inspection error")
        print("Component not found -> skipping")
        return False


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
        if len(text_divs) > 0:
            text_div = text_divs[0]
        else:
            return False
    else:
        return False
    
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



def is_small():
    # detect profile description
    target_divs = driver.find_elements(By.XPATH, '//div[@class="ph5 pb5"]')
    target_div = None
    
    if len(target_divs) > 0:
        target_div = target_divs[0]
    else:
        print("Small check: couldn't find profile description")
        return False
    
    # maybe its a company
    # target specifically the second
    blocks = target_div.find_elements(By.XPATH, './/div[@class="inline-block"]')
    text_div = None
    
    if len(blocks) > 0:
        text_a = blocks[0].find_elements(By.XPATH, "//a[contains(@class, 'org-top-card-summary-info-list__info-item')]")
        
        if len(text_a) > 0:
            text_div = text_a[0]
        else:
            return False
    else:
        return False
    
    # get text and verify keywords
    text = text_div.text
    
    # look for any number K
    numbers_k = re.findall(r'\d+K', text)
    
    if len(numbers_k) > 0:
        # enterprise is too big
        print("Enterprise is too big")
        return False
    
    # find all numbers
    numbers = re.findall(r'\d+', text)
    numbers = [int(n) for n in numbers]
    
    # take maximum
    employee = max(numbers)
    
    print("Number of employee found: ", employee)
    
    return employee < MAX_EMPLOYEE
    

# open file and store data
f = open(FOLLOWUP_FILE, 'a')

# close chat before starting
try:
    close_messages()
except NoSuchElementException:
    print("Couldn't close chat, element doesn't exists")
except ElementClickInterceptedException:
    print("Couldn't close chat, something obscured it")


# establish recursion
def connect(profile):
    
    if len(PROFILES) >= STOP_AT:
        return

    # get the page
    driver.get(profile)
    humanize()

    # phase 1: connect or follow
    try:
        # 
        if find_and_press_connect_button(profile):
            PROFILES.append(profile)
            f.write(profile + '\n')
            print("Connected or followed profile: ", profile)
        else:
            print("Unsuccessful connection on profile: ", profile )
            print("Skipping...")       
        
    except StaleElementReferenceException:
        print("Connecting action error")
        print("Component staled -> skipping")
    except NoSuchElementException:
        print("Connection action error")
        print("Component not found -> skipping")
    except ElementClickInterceptedException:
        print("Connection action error")
        print("Component is obscured")
        
        
    
    filtered_candidates = []
    
    # phase 2: look for other candidates
    try:
            
        results = find_more_results()
        
        if len(results) == 0:
            results = driver.find_elements(By.TAG_NAME, "button")
        
        # collect all profiles
        candidates = collect_links_connect(results) + collect_links_follow(results)
        
        filtered_candidates = list(filter(lambda link: is_matching(link), candidates))   
        
    except StaleElementReferenceException:
        print("Profile retrieval error")
        print("Component staled -> skipping")
        return
    except NoSuchElementException:
        print("Profile retrieval error")
        print("Component not found -> skipping")
        return

    print('\n')
    for candidate in filtered_candidates:
        print("Found candidate:", candidate)
        
    print('\n')
    
    for link in filtered_candidates:
        connect(link)
        

# Execute with a seed

try:
    connect(SEED)
except:
    traceback.print_exc() 
    print("Something went really wrong")
    print("Saving session")


f.close()

print("Algorithm end \n")

    

   
