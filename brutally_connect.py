#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 11:31:14 2024

@author: atlas
"""



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
import os
import numpy as np
from selenium.webdriver.support.ui import Select

# %%Functions preparation


def humanize():
    # better non farsi sgamare
    time.sleep(2.5 + random.uniform(-1,3))
    
    
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

rng = np.random.default_rng()
mu, sigma = 0., 0.1 # mean and standard deviation


# %% Profile info, credentials and parameters

USERNAME = ""
PASSWORD = ""
SIMILARITY_THRESHOLD = 0.8
BROWSER = 'firefox'

LANG = 'en'

PROFILES_FILE = "outputs/company_people"
CONNECTED_FILE = "outputs/company_people_connected"

# %% Open tab

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
            'premium_message' : 'Get Hired with Premium',
            'write_a_message' : 'Write a message…',
            'more_button' : 'More'
            },
        'it' : {
            'connect_button' : 'Collegati',
            'follow_button' : 'Segui',
            'message' : 'Messaggio',
            'send_without_note' : "Invia senza nota",
            'not_now' : "Non ora",
            'italy' : 'Italia',
            'premium_message' : 'Get Hired with Premium',
            'write_a_message' : 'Scrivi un messaggio…',
            'more_button' : 'Altro'
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
WRITE_A_MESSAGE = lang[LANG]['write_a_message']
MORE_BUTTON = lang[LANG]['more_button']

# %% Load profiles

PROFILES = []

# load  visited profiles
with open(PROFILES_FILE) as f:
    PROFILES = [line.rstrip() for line in f]

# remove duplicates
PROFILES = list(set(PROFILES))

# %% Send message

CONNECTED = []

if os.path.isfile(CONNECTED_FILE):

    # load already visited profiles
    with open(CONNECTED_FILE) as f:
        CONNECTED = [line.rstrip() for line in f]


down_click = [Keys.DOWN, Keys.DOWN, Keys.DOWN, Keys.RETURN]        

def scroll_and_click():
    action = ActionChains(driver)
    for key in down_click:
        action.send_keys(key)
        action.pause(max(0.02 + random.uniform(0, 0.3), rng.lognormal(mu, sigma, 1)[0] - 1) ) # umanize action
    action.perform()

def find_and_click_connect_button():
    
    # find main div
    target_divs = driver.find_elements(By.XPATH, '//div[@class="ph5 pb5"]')
    target_div = None
    
    if len(target_divs) > 0:
        target_div = target_divs[0]
    else:
        print("Couldn't find description panel")
        return False
    
    
    # now check if there is a primary or secondary connect button
    all_buttons = target_div.find_elements(By.TAG_NAME, "button")
    
    primary_connect_buttons = [btn for btn in all_buttons if btn.text == CONNECT_BUTTON and "--primary" in btn.get_attribute("class")]
    secondary_connect_buttons = [btn for btn in all_buttons if btn.text == CONNECT_BUTTON and "--secondary" in btn.get_attribute("class")]
    connect_buttons = primary_connect_buttons + secondary_connect_buttons
    
    if len(connect_buttons) > 0:
        # button found
        connect_buttons[0].click()
        humanize()
        return True
    
    # now check is the "More" button is present
    more_buttons = [btn for btn in all_buttons if btn.text == MORE_BUTTON ]
    
    if len(more_buttons) > 0:
        
        # click it
        more_buttons[0].click()
        humanize()
        
        # inspect for content
        # go to the dropdown panel
        dropdowns = target_div.find_elements(By.XPATH, '//div[@class="artdeco-dropdown__content-inner"]')
        
        if len(dropdowns) > 0:
            # find the button with connect
            buttons = dropdowns[0].find_elements(By.XPATH, '//div[contains(@aria-label, "connect")]')
            
            if len(buttons) > 0:
                print("Connect button found")
                
                # use key hack
                scroll_and_click()
                humanize()
            
                return True
            else:
                print("Profile already connected or button is missing")
        
                
    return False

# start sending
for profile in PROFILES:
    
    # skip if already sent
    if profile in CONNECTED:
        continue
    
    # get the page
    driver.get(profile)
    humanize()
    
    # profile  message limit expired check
    try:
        
        button_clicked = find_and_click_connect_button()
        
        if button_clicked:
            
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
            
            # record it it if everything is good
            CONNECTED.append(profile)
        
    except StaleElementReferenceException:
        print("Something went wrong on:", profile)
        print("Connecting action error")
        print("Component staled -> skipping")
    except NoSuchElementException:
        print("Something went wrong on:", profile)
        print("Connection action error")
        print("Component not found -> skipping")
    except ElementClickInterceptedException:
        print("Something went wrong on:", profile)
        print("Connection action error")
        print("Component is obscured")
        
    
# %% Store sent

f = open(CONNECTED_FILE, 'a')
# print results
for p in CONNECTED:
    print(p)
    f.write(p + '\n')
    
f.close()  
