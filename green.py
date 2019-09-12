from selenium import webdriver

from common import Candidate


source = "https://my.greenparty.org.uk/candidates"


def get_candidates():
    driver = webdriver.Chrome()

    candidates = []

    def extract_table():
        table = driver.find_element_by_tag_name("tbody")
        for row in table.find_elements_by_tag_name("tr"):
            cells = row.find_elements_by_tag_name("td")
            link = cells[2].find_element_by_tag_name("a")
            candidates.append(Candidate(constituency=cells[0].text, name=link.text, href=link.get_property("href")))

    try:
        driver.get(source)
        extract_table()
        next_links = driver.find_elements_by_link_text("next ›")
        while next_links:
            next_links[0].click()
            extract_table()
            next_links = driver.find_elements_by_link_text("next ›")
        return candidates
    finally:
        driver.quit()
