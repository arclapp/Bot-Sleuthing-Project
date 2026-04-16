import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



#################### CONSTANTS ####################
SURVEY_URL = "https://uwmadison.co1.qualtrics.com/jfe/form/SV_4G6ZhkhvlltLjQW"


def fill_text(field):
    """
    Fill text input or text area with text.
    """
    field.send_keys("Placeholder")

def fill_radio(radios):
    """
    Select one random radio button. Does nothing if no radios.
    @param radios Radio elements grouped by question
    """
    if len(radios) <= 0:
        return
    
    rand_idx = random.randint(0, len(radios)-1)
    radios[rand_idx].click()

def click_next(driver):
    next_button = driver.find_element(By.ID, "next-button")
    next_button.click()

def main():
    
    driver = webdriver.Chrome()
    driver.get(SURVEY_URL)

    wait = WebDriverWait(driver, 10)

    # Fill text inputs
    text_inputs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input.text-input")))
    text_areas = driver.find_elements(By.CSS_SELECTOR, "textarea.text-input")

    for field in text_inputs + text_areas:
        fill_text(field)

    # Group radios by questions
    questions = driver.find_elements(By.CSS_SELECTOR, "section.question")
    for q in questions:
        radios_per_q = q.find_elements(By.CSS_SELECTOR, "input[type='radio']")

        fill_radio(radios_per_q)


    input("Press Enter to submit the form...")

    # Submit form
    click_next(driver)

    input("Press Enter to close browser...")


if __name__ == "__main__":
    main()