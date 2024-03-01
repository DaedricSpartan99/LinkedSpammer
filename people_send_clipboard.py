

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 22:40:59 2024

@author: atlas
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException

# import Action chains  
from selenium.webdriver.common.action_chains import ActionChains 
import random
from difflib import SequenceMatcher
import os
import numpy as np

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
SENT_FILE = "outputs/company_message_sent"

survey_subject = "Richiesta sondaggio e possibile partnership"

DEBUG = False

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
            'write_a_message' : 'Write a message…'
            },
        'it' : {
            'connect_button' : 'Collegati',
            'follow_button' : 'Segui',
            'message' : 'Messaggio',
            'send_without_note' : "Invia senza nota",
            'not_now' : "Non ora",
            'italy' : 'Italia',
            'premium_message' : 'Get Hired with Premium',
            'write_a_message' : 'Scrivi un messaggio…'
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

# %% Load profiles

PROFILES = []

# load  visited profiles
with open(PROFILES_FILE) as f:
    PROFILES = [line.rstrip() for line in f]

# remove duplicates
PROFILES = list(set(PROFILES))

# %% Send message

SENT = []

if os.path.isfile(SENT_FILE):

    # load already visited profiles
    with open(SENT_FILE) as f:
        SENT = [line.rstrip() for line in f]
        
        
def click_message_button():
    
    success = False
    
    # get the Message button and click it
    all_buttons = driver.find_elements(By.TAG_NAME, "button")
    
    message_buttons = [btn for btn in all_buttons if btn.text == MESSAGE_BUTTON and "--primary" in btn.get_attribute("class")]

    # click message button
    if len(message_buttons) > 0:
        message_buttons[0].click()
        success = True
        
    humanize()
    
    return success
    

def type_subject():
    action = ActionChains(driver)
    for key in survey_subject:
        action.send_keys(key)
        action.pause(max(0.02 + random.uniform(0, 0.3), rng.lognormal(mu, sigma, 1)[0] - 1) ) # umanize action
    action.perform()


def click_text_and_paste():
    # click on message sender
    textfields = driver.find_elements(By.XPATH, '//div[contains(@aria-label,"%s")]' % WRITE_A_MESSAGE)
    
    if len(textfields) > 0:
        textfields[0].click()
        humanize()
    
    action = ActionChains(driver)
    action.key_down(Keys.CONTROL)
    action.send_keys("v")
    action.key_up(Keys.CONTROL)
    action.perform()
    
    
def click_on_submit():
    # submit
    submit = driver.find_element(By.XPATH, "//button[@type='submit']")
        
    # click on submit
    submit.click()
    
    

# start sending
for profile in PROFILES:
    
    # skip if already sent
    if profile in SENT:
        continue
    
    # get the page
    driver.get(profile)
    humanize()
    
    # profile  message limit expired check
    try:
        # find message and click
        if not click_message_button():
            continue
        
        # search a button
        premium_message = driver.find_elements(By.XPATH, "//div[contains(text(), '%s')]" % PREMIUM_MESSAGE)
        
        if len(premium_message) > 0:
            print("Limit reached per account, stopping simulation")
            break
        
        # focus is 
        type_subject()
        humanize()
        
        # click on text field and paste
        click_text_and_paste()
        humanize()
        
        if not DEBUG:
            # click on submit button
            click_on_submit()
            humanize()
        
            # record it it if everything is good
            SENT.append(profile)
        
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

f = open(SENT_FILE, 'a')
# print results
for p in SENT:
    print(p)
    f.write(p + '\n')
    
f.close()  
   
