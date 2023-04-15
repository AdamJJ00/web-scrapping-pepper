import re

import pandas as pd
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

driver = webdriver.Chrome()

driver.get("https://www.pepper.pl")

element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located(
        (By.CSS_SELECTOR, "[data-t='continueWithoutAcceptingBtn']")
    )
)
element.click()

html_content = driver.page_source
df = pd.DataFrame(
    {
        "title": [],
        "price_before_discount": [],
        "price_after_discount": [],
        "hottness": [],
        "comments": [],
    }
)
soup = BS(html_content, "html.parser")
for i in range(1, 5):

    for article in soup.find_all(
        "article",
        {
            "class": "thread cept-thread-item thread--type-list imgFrame-container--scale thread--deal"
        },
    ):
        # wybieram tylko div z pojedynczym artykulem
        lower_div = article.find("div", {"class": "threadGrid thread-clickRoot"})
        # z wyborem hottness jest taki case: albo jest temperatura hot albo burning
        # jak jest hot to sie normalnie ekstraktuje, ale jak jest burning to trzeba w troszke inny sposob stad te zawijasy
        hottness_tag = lower_div.find(
            "span", {"class": "cept-vote-temp vote-temp vote-temp--hot"}
        )
        if hottness_tag is not None:
            hottness_extracted = hottness_tag.get_text()
        else:
            hottness_tag = lower_div.find(
                "span", {"class": "cept-vote-temp vote-temp vote-temp--burn"}
            )
            hottness_extracted = str(hottness_tag)
        hottness = re.search(r"\d+", hottness_tag.get_text()).group()
        # z cenami jest ciekawa sytuacja - czasem jest przed i po znizce
        # czasem jest tylko po znizce, a czasmi nie ma informacji wgl bo to jest jedynie jakas okazja
        prices = lower_div.find("span", {"class": "overflow--fade"})
        try:
            price_after_discount = prices.find(
                "span",
                {"class": "thread-price text--b cept-tp size--all-l size--fromW3-xl"},
            ).get_text()
            price_before_discount_tag = prices.find(
                "span",
                {"class": "mute--text text--lineThrough size--all-l size--fromW3-xl"},
            )
            if price_before_discount_tag is not None:
                price_before_discount = price_before_discount_tag.get_text()
            else:
                price_before_discount = "price not available"
        except AttributeError:
            price_after_discount = "price not available"
            price_before_discount = "price not available"
        # przy insertowaniu do df trzeba bedzie obsluzyc 'za darmo' jako cene po obnizce
        comments = lower_div.find(
            "a",
            {
                "class": "button button--type-secondary button--mode-default button--shape-circle"
            },
        ).get_text()
        title = lower_div.find("strong", {"class": "thread-title"}).find("a")["title"]
        bargain_info = {
            "title": title,
            "price_before_discount": price_before_discount,
            "price_after_discount": price_after_discount,
            "hottness": hottness,
            "comments": comments,
        }
        df = df.append(bargain_info, ignore_index=True)
    driver.get(f"https://www.pepper.pl/?page={i+1}")
    html_content = driver.page_source
    soup = BS(html_content, "html.parser")

# driver.quit()
