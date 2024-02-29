from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time

# import Action chains  
from selenium.webdriver.common.action_chains import ActionChains 


"""
    Functions preparation
"""

def humanize():
    # TODO: better non farsi sgamare
    time.sleep(2)

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

"""
    Profile message request and send after response
"""

PROFILES = [
        "https://www.linkedin.com/in/emanuele-sorgente-331478228/",
        "https://www.linkedin.com/in/alessia-bernareggi/"
        ]

for profile in PROFILES:

    # get the page
    driver.get(profile)
    humanize()

    # get the Message button and click it
    all_buttons = driver.find_elements(By.TAG_NAME, "button")

    message_buttons = [btn for btn in all_buttons if btn.text == "Message"]

    message_buttons[0].click()

    humanize()

    # access to message input container
    
    main_div = driver.find_element("xpath", '//*[@id="ember3084"]')
    main_div.click()

    humanize()
    
    
    # get the input paragraph
    paragraphs = driver.find_elements(By.TAG_NAME, "p")

    counter = 0
    for p in paragraphs:
        print(counter, ":", p.text)
        counter += 1
    #paragraphs[-5].send_keys("Invio automatico script python")
    
    action = ActionChains(driver)
    action.key_down(Keys.CONTROL)
    action.send_keys("v")
    action.key_up(Keys.CONTROL)
    action.perform()

    humanize()

    # submit
    submit = driver.find_element("xpath", "//button[@type='submit']").click()
    
    humanize()
    
    
