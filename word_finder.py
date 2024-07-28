from urllib import parse
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import pandas as pd


class WordFinder:
    def __init__(self, driver):
        self.driver = driver

    def find_name(self):
        """Retrieves genitive singular, partitive singular and partitive plural
        from the declination table under 'https://fi.wiktionary.org/wiki/{word}'"""
        # word_link = parse.quote_plus(f"https://fi.wiktionary.org/wiki/{word}", "/:?=&")
        try:
            flextion_table = [table for table in pd.read_html(self.driver.current_url) if ("Taivutus" in table.head())][0]
        except (NoSuchElementException, IndexError, ValueError):
            return None
        else:
            genitive = flextion_table.iloc[1, 1]
            part_sing = flextion_table.iloc[2, 1]
            part_plural = flextion_table.iloc[2, 2]
            return ", ".join([genitive, part_sing, part_plural])

    def find_composed_name(self):
        """Search in the page if information is provided on composed words: if the current word is a composed word
        and information is provided on the single words, the declination of the last word is provided"""
        try:
            composed_word_description = (self.driver.find_element
                                         (By.XPATH, value="//*[contains(text(),'yhdyssana')]"))
            composed_word_last_word = (composed_word_description
                                       .find_element(By.CSS_SELECTOR, value="i:last-of-type a")
                                       .get_attribute("title"))
            word_link = parse.quote_plus(f"https://fi.wiktionary.org/wiki/{composed_word_last_word}",
                                         "/:?=&")
            flextion_table = [table for table in pd.read_html(word_link)
                              if ("Taivutus" in table.head())][0]
        except (NoSuchElementException, IndexError, ValueError):
            return None
        else:
            genitive = flextion_table.iloc[1, 1]
            part_sing = flextion_table.iloc[2, 1]
            part_plural = flextion_table.iloc[2, 2]
            return ", ".join([genitive, part_sing, part_plural])

    def find_verb(self):
        """Extracts the first person indicative present, first person indicative perfect
        and past participle of the verb"""
        try:
            link_to_declination = self.driver.find_element(By.LINK_TEXT, value="taivutus").get_attribute("href")
            indicative_table = [table for table in pd.read_html(link_to_declination)
                                if ("Indikatiivi" in table.head())][0]
        except (NoSuchElementException, IndexError, ValueError):
            return None
        else:
            first_persons = indicative_table["Indikatiivi"]["preesens"] \
                .loc[indicative_table["Indikatiivi"]["preesens"]["persoona"] == "minä"]
            fist_person_present = first_persons["myönteinen"][0]
            fist_person_past = first_persons["myönteinen"][10]

            perfect = indicative_table["Indikatiivi"]["perfekti"] \
                .loc[indicative_table["Indikatiivi"]["perfekti"]["persoona"] == "minä"]
            participle = perfect["myönteinen"][0].split()[1]
            return ", ".join([fist_person_present, fist_person_past, participle])

    def find_adjective(self):
        """Tries to retrieve genitive singular, partitive singular and partitive plural
        from the declention table under 'https://fi.wiktionary.org/wiki/{word}'"""
        try:
            link_to_declination = self.driver.find_element(By.LINK_TEXT, value="taivutus").get_attribute("href")
            adjective_table = [table for table in pd.read_html(link_to_declination)
                               if ("Positiivi" in table.head())][0]
        except (NoSuchElementException, IndexError, ValueError):
            return None
        else:
            genitive_sing = adjective_table["Positiivi"]["yksikkö"][1]
            partitive_sing = adjective_table["Positiivi"]["yksikkö"][2]
            partitive_plur = adjective_table["Positiivi"]["monikko"][2]

            return ", ".join([genitive_sing, partitive_sing, partitive_plur])

# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_experimental_option("detach", True)
#
# driver = webdriver.Chrome(options=chrome_options)
#
# word_link = parse.quote_plus(f"https://fi.wiktionary.org/wiki/tiivis", "/:?=&")
# driver.get(word_link)
# print(find_adjective(driver))
