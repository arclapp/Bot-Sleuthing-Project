from GPT import GPT

import random
from typing import Union, Callable

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException


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


# def fill_text(field: webdriver.remote.webelement.WebElement, question:str, llm_agent:GPT) -> None:
#     """
#     Fill a text input or textarea with text generated using LLM. If question
#     or llm_agent are None, defaults to filling with "Placeholder"

#     Args:
#         field: The input or textarea element to fill.
#         question: Question statement associated with text field. 
#         llm: LLM agent to use
#     """
#     if not field:
#         return

#     field_text = "Placeholder"
#     if question and llm_agent:
#         field_text = llm_agent.prompt(question)
#         print("LLM:", field_text)
    
#     field.send_keys(field_text)

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


def click_next(driver: webdriver.Chrome) -> None:
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

        questions = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "section.question")))
        for i in range(len(questions)):
            q = driver.find_elements(By.CSS_SELECTOR, "section.question")[i]
            q_text = q.find_element(By.CSS_SELECTOR, ".question-display").text
            print("QUESTIONS", q_text)

            # Agent response to question
            agent_response = "PLACEHOLDER"
            text_inputs = q.find_elements(By.CSS_SELECTOR, "input.text-input, textarea.text-input")
            if text_inputs:                                                                                                                                                                                           
                agent_response = llm_agent.prompt(q_text)                                       
                print("ANSWER:", agent_response)                                                                                                                                                                      
            
            # Refresh so not stale
            q = driver.find_elements(By.CSS_SELECTOR, "section.question")[i]
            loop_through_elements(q, "input.text-input", fill_text, agent_response)                                                                                                                               
            loop_through_elements(q, "textarea.text-input", fill_text, agent_response)  

            # Group radios by questions
            radios_per_q = q.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            fill_radio(radios_per_q)


        input("Press Enter to move to the next page")
        try:
            click_next(driver)
        except:
            print("Reached end of survey")
            break


    input("Press Enter to close browser...")


if __name__ == "__main__":
    main()