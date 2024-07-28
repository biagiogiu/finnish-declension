import os
import json
import requests
from urllib import parse
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from word_finder import WordFinder

# set url and headers for sheety endpoint
sheet_endpoint = os.environ["SHEET_ENDPOINT"]
token = os.environ["TOKEN"]

sheety_header = {
    "Authorization": f"Bearer {token}"
}

#fetch the csv from sheety and save it in a json file
response = requests.get(url=sheet_endpoint, headers=sheety_header)
response.raise_for_status()
csv = response.json()
with open("word_list.json", "w", encoding="UTF-8") as f:
    json.dump(csv, f, ensure_ascii=False, indent=4)

with open("word_list.json", "r", encoding="UTF-8") as f:
    word_list_csv = json.load(f)

# generate the list of words to be searched
finnish_words = [word for word in word_list_csv["words"]]

# set the webdriver with Selenium
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)
# initialize the word finder
finder = WordFinder(driver)

for word in finnish_words:
    # if the declination hasn't been filled out yet, search for it in wikitionary
    if word["declinazione"] == "":
        declination = ""
        try:
            word_link = parse.quote_plus(f"https://fi.wiktionary.org/wiki/{word['suomi']}", "/:?=&")
            driver.get(word_link)
        except NoSuchElementException:
            print(f"problem with {word['suomi']}: NoSuchElementException")
        else:
            try:
                word_type = driver.find_element(By.CSS_SELECTOR, value="h3 span.mw-headline").get_attribute("id")
            except NoSuchElementException:
                pass
            else:
                # if the word is found in wikitionary, extract the declination
                # based on part of speech (name, adjective, verb)
                if word_type == "Substantiivi" or word_type == "Pronomini":
                    declination = finder.find_name()
                    if declination is None:
                        declination = finder.find_composed_name()
                        if declination is None:
                            declination = finder.find_verb()
                if word_type == "Verbi":
                    declination = finder.find_verb()

                if word_type == "Adjektiivi":
                    declination = finder.find_adjective()

            # save the declination in the csv sheety
            if declination is not None:
                new_declination = {"word": {"declinazione": declination}}
                response = requests.put(f"{sheet_endpoint}/{word['id']}", json=new_declination, headers=sheety_header)

driver.quit()
