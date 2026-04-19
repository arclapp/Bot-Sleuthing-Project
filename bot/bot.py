from GPT import GPT

import random
from typing import Union, Callable
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup


################################## CONSTANTS ##################################
SURVEY_URL = "https://uwmadison.co1.qualtrics.com/jfe/form/SV_4G6ZhkhvlltLjQW"
USE_LLM_AGENT = True
################################################################################

def generate_llm_agent() -> GPT:
    """
    Returns:
        LLM ("gpt-5-nano") agent prompted with role description.
    """
    MODEL = "gpt-5-nano"
    AGENT_DESCRIPTION = ("You an agent used as an automated bot to test " \
                "the security of a survey. Make sure to ONLY return 1-2 sentences max that " \
                "answer the questions as an average person would.")
    
    llm_agent = GPT(AGENT_DESCRIPTION, MODEL)
    return llm_agent



def fill_text(field: webdriver.remote.webelement.WebElement, text:str) -> None:
    """
    Fill a text input or textarea with text.

    Args:
        field: The input or textarea element to fill.
        question: Question statement associated with text field. 
        text: Text to fill into the field
    """
    if not field:
        return
    
    field.send_keys(text)


def fill_radio(radios: list[webdriver.remote.webelement.WebElement]) -> None:
    """
    Select one random radio button from a list. Does nothing if the list is empty.

    Args:
        radios: Radio button elements from a single question group.
    """
    if len(radios) <= 0:
        return

    rand_idx = random.randint(0, len(radios)-1)
    radios[rand_idx].click()

def fill_slider(slider: list[webdriver.remote.webelement.WebElement], driver:webdriver.remote.webdriver.WebDriver) -> None:
    """
    Select random slider value (between min and max)

    Args:
        radios: Slider element
    """
    min_val = int(slider.get_attribute("min"))
    max_val = int(slider.get_attribute("max"))

    rand_val = random.randint(min_val, max_val)

    driver.execute_script("arguments[0].value = arguments[1];", slider, rand_val)
    driver.execute_script(
        "arguments[0].dispatchEvent(new Event('input', {bubbles: true})); "
        "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
        slider
    )     

def click_next(driver: webdriver.remote.webdriver.WebDriver  ) -> None:
    """
    Click the next/submit button to advance to the next survey page.

    Args:
        driver: The Selenium WebDriver instance controlling the browser.
    """
    next_button = driver.find_element(By.ID, "next-button")
    next_button.click()


def loop_through_elements(root: Union[webdriver.remote.webdriver.WebDriver, webdriver.remote.webelement.WebElement], 
                          css_selector:str, fn: Callable, *args, **kwargs):
    """
    Loops through elements while preventing stale element reference. For each element found, applies 
    the provided function `fn`, passing the element as the first argument followed by any 
    additional positional and keyword arguments.

    Args:
        root (WebDriver | WebElement): The search context to locate elements within (e.g., the browser
            driver or a parent DOM element).
        css_selector: CSS selector used to locate target elements within the root.
        fn: Function to apply to each element. Must accept the element as its
            first parameter.
        *args/**kwargs: Additional positional/keyword arguments passed to `fn`.
    """
    elements = root.find_elements(By.CSS_SELECTOR, css_selector)

    for i in range(len(elements)):

        # Re-fetch fresh element
        fresh_elements = root.find_elements(By.CSS_SELECTOR, css_selector)
        elem = fresh_elements[i]

        fn(elem, *args, **kwargs)



def main() -> None:
    """
    Launch the browser, fill out the survey form, and submit it.
    """


    # Initialize LLM Agent
    llm_agent = None
    if USE_LLM_AGENT:
        llm_agent = generate_llm_agent()
        
    driver = webdriver.Chrome()
    driver.get(SURVEY_URL)

    wait = WebDriverWait(driver, 10)

    
    
    
    while True:
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        with open("survey_page.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())   

        QUESTION_SECTION_SELECTOR = "section[id^='question-']"
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, QUESTION_SECTION_SELECTOR)))

        # Iterate through all questions (handles branching)
        i = -1
        while True:
            i += 1
            questions = [q for q in driver.find_elements(By.CSS_SELECTOR, QUESTION_SECTION_SELECTOR) if q.is_displayed()]
            if i >= len(questions):
                break
            q = questions[i]

            
            QUESTION_TEXT_SELECTOR = "div[id^='question-display-']"
            q_text_els = q.find_elements(By.CSS_SELECTOR, QUESTION_TEXT_SELECTOR)
            if not q_text_els:
                continue
            q_text = q_text_els[0].text


            # Agent response to question
            agent_response = "PLACEHOLDER"
            text_inputs = q.find_elements(By.CSS_SELECTOR, "input.text-input, textarea.text-input")
            if text_inputs:
                agent_response = llm_agent.prompt(q_text)
            
            # Refresh so not stale
            q = [q for q in driver.find_elements(By.CSS_SELECTOR, QUESTION_SECTION_SELECTOR) if q.is_displayed()][i]
            loop_through_elements(q, "input.text-input", fill_text, agent_response)
            loop_through_elements(q, "textarea.text-input", fill_text, agent_response)

            # Group radios by rows if matrix, else by question
            QUESTION_RADIO_SELECTOR = "input[type='radio']"
            rows = q.find_elements(By.CSS_SELECTOR, ".matrix-row")                                                                                                                                                                                                                                            
            if rows:                                                                                                                                                                                                                                                                                          
                for row in rows:
                    fill_radio(row.find_elements(By.CSS_SELECTOR, QUESTION_RADIO_SELECTOR))                                                                                                                                                                                                                     
            else:                                                                                                                                                                                                                                                                                           
                fill_radio(q.find_elements(By.CSS_SELECTOR, QUESTION_RADIO_SELECTOR))

            # Get slider
            slider = q.find_elements(By.CSS_SELECTOR, "input[type='range']")
            if slider:
                slider = slider[0]
                fill_slider(slider, driver)




        input("Press Enter to move to the next page")
        try:
            click_next(driver)
        except:
            print("Reached end of survey")
            break


    input("Press Enter to close browser...")


if __name__ == "__main__":
    main()