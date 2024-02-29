#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 08:14:43 2024

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
from selenium.common.exceptions import StaleElementReferenceException

import re
import random

# %% Auth and browser informations

"""
    Driver section
"""
driver = webdriver.Firefox()

"""
    Login section
"""

USERNAME = ""
PASSWORD = ""
ALREADY_LOGGED_IN = False

# %% Functions preparation


def humanize():
    # better non farsi sgamare
    time.sleep(1.5 + random.uniform(0,1))

# %% Login process

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
    

# %%Search new profiles

PROFILES = []

STOP_AT = 20
SEED ="https://www.linkedin.com/in/massimociuffreda/"

survey_subject = "Survey for digital nomads"

DEBUG = False

# %% Connect to profiles

def type_subject():
    action = ActionChains(driver)
    for key in survey_subject:
        action.send_keys(key)
        action.pause(0.05 + random.uniform(0, 0.5)) # umanize action
    action.perform()
    

def follow_and_send(profile):
    
    if len(PROFILES) >= STOP_AT:
        return

    # get the page
    driver.get(profile)
    humanize()

    try:
        # get connect button 
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        
        follow_buttons = [btn for btn in all_buttons if btn.text == "Segui" and "--primary" in btn.get_attribute("class")]
        
        if len(follow_buttons) > 0:
            print("Found follow button: ", follow_buttons[0].get_attribute("id"))
            
            if not DEBUG:
                follow_buttons[0].click()
                
            PROFILES.append(profile)
            humanize()
            
            # restore page
            buttons = driver.find_elements(By.TAG_NAME, "button")
            not_now = [btn for btn in buttons if btn.text == "Non ora"]
            if len(not_now) > 0:
                not_now[0].click()
                humanize()
                
        # send message copied in clipboard
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        message_buttons = [btn for btn in all_buttons if btn.text == "Messaggio"]
        
        message_buttons[0].click()
        humanize()
        
        # write into subject
        type_subject()
        
        # click on message sender
        textfields = driver.find_elements(By.XPATH, '//div[@aria-label="Scrivi un messaggio…"]')
        
        if len(textfields) > 0:
            textfields[0].click()
            humanize()
        
        action = ActionChains(driver)
        action.key_down(Keys.CONTROL)
        action.send_keys("v")
        action.key_up(Keys.CONTROL)
        action.perform()

        humanize()
        
        submits = driver.find_elements("xpath", "//button[@type='submit']")
        
        if len(submits) > 0:
            if not DEBUG:
                submits[0].click()
            humanize()
        else:
            print("Could not find submit button on profile: ", profile)
            
        # close message stuff
        divs = driver.find_elements(By.XPATH, '//div[contains(@class,"msg-overlay-bubble-header__controls")]')
        for div in divs:

            # find close button
            buttons = div.find_elements(By.XPATH, './/button[@artdeco-button--tertiary]')
            for button in buttons:
                # find specific tag making sure it is the close button
                uses = button.find_elements(By.XPATH, './/use[@href="#close-small"]')
                print("Found close buttons: ", uses)
                # if use is present
                if len(uses) > 0:
                    button.click()
                    humanize()
                    break
        
        # search other followable people
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        spread_buttons = [btn for btn in all_buttons if btn.text == "Segui" and "--secondary" in btn.get_attribute("class")]
        
            
        print("Spread button found: ", len(spread_buttons))
        # spread algorithm until
        for button in spread_buttons:
            # get profile name
            label = button.get_attribute("aria-label")
            regex = re.compile(r"Segui (.*)")
            name = regex.search(label).group(1)
            print("Spread name: ", name)
            
            # search other profile link
            divs = button.find_elements(By.XPATH, './/ancestor::div[@data-view-name="profile-component-entity"]')
            if len(divs) > 0:
                div = divs[0]
                a = div.find_element(By.XPATH, './/a[@href]')
                link = a.get_attribute("href")
            
                # if everything is fine recurse
                if (link not in PROFILES):
                    print("Spread link: ", link)
                    follow_and_send(link)
                
    except StaleElementReferenceException:
        print("Component staled")
        return
    except NoSuchElementException:
        print("Component not found")
        return
        

# Execute with a seed
follow_and_send(SEED)

# %% Store profiles
print(PROFILES)
    
