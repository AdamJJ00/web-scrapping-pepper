import re

import pandas as pd
from bs4 import BeautifulSoup as BS
from bs4.element import Tag
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class PepperScrapper:
    def __init__(self, driver: webdriver):
        self.web_driver = driver
        self.current_page = 1
        self.current_soup = None
        self.click_on_continue_without_cookies()
        self.scrapped_data = pd.DataFrame(
            {col: [] for col in self.get_columns_for_content_df()}
        )
        self.derive_html_content_from_driver_to_soup()

    def click_on_continue_without_cookies(self) -> None:
        element = WebDriverWait(self.web_driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[data-t='continueWithoutAcceptingBtn']")
            )
        )
        element.click()

    @staticmethod
    def get_columns_for_content_df() -> list:
        return [
            "title",
            "price_before_discount",
            "price_after_discount",
            "hottness",
            "comments",
        ]

    def derive_html_content_from_driver_to_soup(self) -> None:
        html_content = self.web_driver.page_source
        self.current_soup = BS(html_content, "html.parser")

    def scan_and_add_current_page_for_content(self) -> None:
        self.scrapped_data = pd.concat(
            [
                self.scrapped_data,
                pd.DataFrame(
                    [
                        self.extract_content_from_article(article)
                        for article in self.current_soup.find_all(
                            self.get_properties_for_dividing_page_to_articles()
                        )
                    ],
                    columns=self.get_columns_for_content_df(),
                ),
            ]
        )

    @staticmethod
    def get_properties_for_dividing_page_to_articles() -> tuple:
        return "article", {
            "class": "thread cept-thread-item thread--type-list imgFrame-container--scale thread--deal"
        }

    def extract_content_from_article(self, article: Tag) -> list:
        content_div = article.find("div", {"class": "threadGrid thread-clickRoot"})
        # if content_div is none, then the bargain will open up tomorrow, so we select it by different tag
        if content_div is None:
            content_div = article.find(
                "div", {"class": "thread-fullMode threadGrid thread-clickRoot"}
            )
        hottness = self.extract_hottness(content_div)
        price_before_discount, price_after_discount = self.extract_prices(content_div)
        comments = self.extract_comments(content_div)
        title = self.extract_title(content_div)
        return [title, price_before_discount, price_after_discount, hottness, comments]

    @staticmethod
    def extract_hottness(bargain_div: Tag) -> int:
        # there are 3 types of hottness: hot, burning and expired
        hottness_tag = bargain_div.find(
            "span", {"class": "cept-vote-temp vote-temp vote-temp--hot"}
        )
        # case 1 - bargain is "hot" and we can extract the text easily
        if hottness_tag and (
            "hot" in hottness_tag["class"] or "vote-temp--hot" in hottness_tag["class"]
        ):
            hottness_extracted = hottness_tag.get_text()
        # case 2 - bargain is "burning" and we can access the text straight from text
        if not hottness_tag:
            hottness_tag = bargain_div.find(
                "span", {"class": "cept-vote-temp vote-temp vote-temp--burn"}
            )
            hottness_extracted = str(hottness_tag)
        # case 3 - bargain is expired and we can access the hottness by other div tag
        if not hottness_tag:
            hottness_tag = bargain_div.find("span", {"class": "space--h-2 text--b"})
            hottness_extracted = hottness_tag.get_text()
        hottness = (
            re.search(r"\d+", hottness_extracted).group()
            if hottness_extracted is not None
            else -1
        )
        return int(hottness)

    @staticmethod
    def extract_prices(bargain_div: Tag) -> tuple:
        prices = bargain_div.find("span", {"class": "overflow--fade"})
        # try to extract prices: sometimes, the price before discount tag is not present
        # there are also situations where there are no prices at all
        # and users just upload a bargain for other users to explore on their own
        try:
            # try to find price after discount - if it is not present, then is is just a bargain
            # or a link to a webpage for other users to explore on their own
            price_after_discount = prices.find(
                "span",
                {"class": "thread-price text--b cept-tp size--all-l size--fromW3-xl"},
            ).get_text()
            price_before_discount_tag = prices.find(
                "span",
                {"class": "mute--text text--lineThrough size--all-l size--fromW3-xl"},
            )
            # if price_before_discount_tag is None, then there is no price before discount
            if price_before_discount_tag is not None:
                price_before_discount = price_before_discount_tag.get_text()
            else:
                price_before_discount = "price not available"
        except AttributeError:
            price_after_discount = "price not available"
            price_before_discount = "price not available"
        return price_before_discount, price_after_discount

    @staticmethod
    def extract_comments(bargain_div: Tag) -> int:
        comments = bargain_div.find(
            "a",
            {
                "class": "button button--type-secondary button--mode-default button--shape-circle"
            },
        ).get_text()
        if comments != "":
            return int(comments)
        else:
            print(bargain_div)
            return -1

    @staticmethod
    def extract_title(bargain_div: Tag) -> str:
        return bargain_div.find("strong", {"class": "thread-title"}).find("a")["title"]

    def scan_next_pages(self, pages_to_scan: int = 5):
        for page in range(pages_to_scan):
            self.current_page += 1
            self.web_driver.get(self.get_url_for_page(self.current_page))
            self.derive_html_content_from_driver_to_soup()
            self.scan_and_add_current_page_for_content()

    @staticmethod
    def get_url_for_page(page_num: int):
        return f"https://www.pepper.pl/?page={page_num}"


if __name__ == "__main__":
    driver = webdriver.Chrome()
    driver.get("https://www.pepper.pl")
    scrapper = PepperScrapper(driver=driver)
    scrapper.scan_and_add_current_page_for_content()
    scrapper.scan_next_pages()
