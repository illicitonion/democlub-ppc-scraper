from selenium import webdriver

from common import Candidate


def from_card(card):
    link = card.find_element_by_tag_name("a")
    href = link.get_property("href")
    constituency = link.find_element_by_class_name("card-title").text
    name = link.find_element_by_class_name("card-meta").text.strip()
    return Candidate(href=href, constituency=constituency, name=name)


def is_candidate(driver, candidate):
    driver.get(candidate.href)
    h2 = driver.find_element_by_tag_name("h2")
    # Sadly there doesn't appear to be a way to find current MPs who are also candidates :(
    return "Candidate" in h2.text


def get_candidates():
    driver = webdriver.Chrome()
    try:
        driver.get("http://vote.labour.org.uk/all-candidates")
        cards = driver.find_elements_by_css_selector("li.card")
        candidates = [from_card(card) for card in cards]
        without_mps = [c for c in candidates if is_candidate(driver, c)]
        return without_mps
    finally:
        driver.quit()
