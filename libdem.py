from selenium import webdriver

from common import Candidate


def get_candidates():
    driver = webdriver.Chrome()

    try:
        driver.get("https://www.markpack.org.uk/153722/liberal-democrat-parliamentary-candidates/")
        uls = driver.find_elements_by_tag_name("ul")[:5]
        lis = []
        for ul in uls:
            lis.extend(ul.find_elements_by_tag_name("li"))
        for li in lis:
            text = li.text
            parts = text.split(": ")
            constituency, name = parts[0], parts[-1]
            if constituency == "Richmond (Yorkshire)":
                constituency = "richmond-yorks"
            if " (" in constituency:
                constituency = constituency[: constituency.find(" (")]
            if constituency.endswith(" constituency"):
                constituency = constituency[:-13]

            if " (" in name:
                name = name[: name.find(" (")]
            yield Candidate(name=name, constituency=constituency, href=None)
    finally:
        driver.quit()
