from GPT import GPT

import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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


def fill_text(field: webdriver.remote.webelement.WebElement, llm_agent:GPT) -> None:
    """
    Fill a text input or textarea with text.

    Args:
        field: The input or textarea element to fill.
        llm: LLM agent to use
    """

    llm_agent.prompt("Say hello in one sentence.")
    field.send_keys("Placeholder")


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