
from selenium import webdriver
from bs4 import BeautifulSoup

SURVEY_URL = "https://uwmadison.co1.qualtrics.com/jfe/form/SV_4G6ZhkhvlltLjQW"




driver = webdriver.Chrome()
driver.get(SURVEY_URL)

soup = BeautifulSoup(driver.page_source, "html.parser")
formatted_soup = soup.prettify()
print(formatted_soup)
with open("page_output.txt", "w") as file:
    file.write(formatted_soup)
