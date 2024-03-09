

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
import traceback, sys

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

LANG = 'it'

PROFILES_FILE = "outputs/company_people_connected"
SENT_FILE = "outputs/company_message_sent"

survey_subject = "Richiesta sondaggio e possibile partnership"

DEBUG = False

MESSAGE_FILE = 'messages/aziende.txt'

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
            'show_more' :  'Show more results'
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
            'show_more' : 'Mostra altri risultati'
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
SHOW_MORE = lang[LANG]['show_more']

# %% Load profiles

PROFILES = []

# load  visited profiles
with open(PROFILES_FILE) as f:
    PROFILES = [line.rstrip() for line in f]

# remove duplicates
PROFILES = set(PROFILES)

# %% Scan connected profiles

# go to connections
driver.get('https://www.linkedin.com/mynetwork/invite-connect/connections/')
humanize()

# scroll down until end
def pagedown():
    action = ActionChains(driver)
    action.key_down(Keys.CONTROL)
    action.send_keys(Keys.DOWN)
    action.key_up(Keys.CONTROL)
    action.perform()
    
def click_show_more_if_there():
    all_buttons = driver.find_elements(By.TAG_NAME, "button")
    show_more = [btn for btn in all_buttons if btn.text == SHOW_MORE]
    
    if len(show_more) > 0:
        show_more[0].click()
        humanize()
        return True
    
    return False

def scan_profiles():
    lis = driver.find_elements(By.XPATH, "//li[contains(@class, 'mn-connection-card')]")
    
    link_list = []
    
    for li in lis:
        a = li.find_element(By.XPATH, './/a[@href]')
    
        # get full link
        link = a.get_attribute("href")
        
        link_list.append(link)
        
    return link_list


CONNECTIONS = set([])   

while True:
    
    try:
        # scroll down
        pagedown()
        
        # scan for new profiles
        profiles = set(scan_profiles())
        
        # no profiles added from previous step
        if len(profiles) == len(CONNECTIONS):
        
            # check if there is the button
            if click_show_more_if_there():
                print("Clicking more results")
                pass
            else:
                # stop the algorithm
                print("No more available profiles, stop")
                break
        else:
            # set new state
            CONNECTIONS = profiles
            print("Setting new state")
            
            for p in CONNECTIONS:
                print(p)
                
            print('\n')
            
    except:
        print("Something went wrong, restarting process")
        driver.get('https://www.linkedin.com/mynetwork/invite-connect/connections/')
        humanize()
        CONNECTIONS = set([])
        
# print final state connection

# %% Load already sent profiles

SENT = []

if os.path.isfile(SENT_FILE):

    # load already visited profiles
    with open(SENT_FILE) as f:
        SENT = [line.rstrip() for line in f]

SENT = set(SENT)

# %% Apply intersection between profiles and actual connections

# get only connected profiles and non sent
TARGET = PROFILES.intersection(CONNECTIONS).difference(SENT)

# print target

print("Targetting profiles: \n")
for t in TARGET:
    print(t)
    
print('\n')

# %% Open a pastebin and make sure the message is put into the clipboard

driver.get('https://pastebin.com/')
humanize()

textarea = None

try:
    textarea = driver.find_element(By.XPATH, "//textarea[@id='postform-text']")
    
except NoSuchElementException:
    print("Can't find element for paste, must stop")
    
# click on it and obtain focus
textarea.click()
humanize()
    
MESSAGE = []

# read text
with open(MESSAGE_FILE) as f:
    MESSAGE = f.readlines()
    
# inject message
for line in MESSAGE:
    textarea.send_keys(line)

def select_all():
    action = ActionChains(driver)
    action.key_down(Keys.CONTROL)
    action.send_keys("a")
    action.key_up(Keys.CONTROL)
    action.perform()
    
def copy():
    action = ActionChains(driver)
    action.key_down(Keys.CONTROL)
    action.send_keys("c")
    action.key_up(Keys.CONTROL)
    action.perform()
    
# select message
select_all()
humanize()

# copy into clipboard
copy()
humanize()


# %% Send message
        
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


def paste():
    # click on message sender 
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
    
# log in place
f = open(SENT_FILE, 'a')

# start sending
for profile in TARGET:
    
    # get the page
    driver.get(profile)
    humanize()
    
    # profile  message limit expired check
    try:
        # find message and click
        if not click_message_button():
            print("Message button not clicked, check the LANG parameter or other")
            continue
        
        
        # click on text field and paste
        paste()
        humanize()
        
        if not DEBUG:
            # click on submit button
            click_on_submit()
            humanize()
        
            # record it it if everything is good
            SENT.append(profile)
            f.write(profile + '\n')
        
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
    except:
        print("Something else went wrong on:", profile)
        print("Saving session")
        # printing stack trace 
        traceback.print_exc() 
        # stop algorithm
        break
        
f.close()  

   
