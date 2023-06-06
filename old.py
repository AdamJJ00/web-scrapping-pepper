import getpass
import re
import time

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
        self.login_to_pepper()
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
            "username",
            "link",
        ]

    def derive_html_content_from_driver_to_soup(self) -> None:
        html_content = self.web_driver.page_source
        self.current_soup = BS(html_content, "html.parser")

    def scan_current_page_for_content(self) -> None:
        self.scrapped_data = pd.concat(
            [
                self.scrapped_data,
                pd.DataFrame(
                    [
                        self.extract_content_from_article(article)
                        for article in self.current_soup.find_all("article")
                    ],
                    columns=self.get_columns_for_content_df(),
                ),
            ]
        )

    def extract_content_from_article(self, article: Tag) -> list:
        content_div = article.find(
            "div", {"class": "threadGrid thread-clickRoot"}
        )
        if content_div is None:
            content_div = article.find(
                "div", {"class": "thread-fullMode threadGrid thread-clickRoot"}
            )
        if content_div is None:
            content_div = article.find("div", {"class": ""})
        title, link = self.extract_title(content_div)
        hottness = self.extract_hottness(content_div)
        price_before_discount, price_after_discount = self.extract_prices(
            content_div
        )
        comments = self.extract_comments(content_div)
        username = self.extract_username(content_div)
        return [
            title,
            price_before_discount,
            price_after_discount,
            hottness,
            comments,
            username,
            link,
        ]

    @staticmethod
    def extract_hottness(bargain_div: Tag) -> int:
        hottness_tag = bargain_div.find(
            "div",
            {
                "class": "cept-vote-box vote-box overflow--hidden border border--color-borderGrey bRad--a thread-noClick"
            },
        )
        if hottness_tag:
            hottness_extracted = hottness_tag.get_text()
        else:
            hottness_tag = bargain_div.find(
                "div",
                {
                    "class": "vote-box vote-box--muted space--h-2 border border--color-borderGrey bRad--a text--color-grey space--mr-3"
                },
            )
            hottness_extracted = hottness_tag.get_text()
        try:
            hottness = re.search(r"\d+", hottness_extracted).group()
        except AttributeError:
            hottness = -1
        return hottness

    @staticmethod
    def extract_username(bargain_div: Tag) -> str:
        return (
            bargain_div.find("span", {"class": "thread-username"})
            .get_text()
            .strip("\n\t")
        )

    @staticmethod
    def extract_prices(bargain_div: Tag) -> tuple:
        prices = bargain_div.find("span", {"class": "overflow--fade"})
        try:
            price_after_discount = prices.find(
                "span",
                {"class": "overflow--wrap-off"},
            ).get_text()
        except AttributeError:
            price_after_discount = "price not available"
        price_before_discount_tag = prices.find(
            "span",
            {"class": "flex--inline boxAlign-ai--all-c space--ml-2"},
        )
        try:
            price_before_discount = price_before_discount_tag.find(
                "span"
            ).get_text()
        except AttributeError:
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
            return -1

    @staticmethod
    def extract_title(bargain_div: Tag) -> str:
        title_anchor = bargain_div.find(
            "strong", {"class": "thread-title"}
        ).find("a")
        return title_anchor["title"], title_anchor["href"]

    def scan_next_pages(self, pages_to_scan: int = 5):
        for page in range(pages_to_scan):
            self.current_page += 1
            self.web_driver.get(self.get_url_for_page(self.current_page))
            self.derive_html_content_from_driver_to_soup()
            self.scan_current_page_for_content()

    @staticmethod
    def get_url_for_page(page_num: int):
        return f"https://www.pepper.pl/?page={page_num}"

    def login_to_pepper(self):
        time.sleep(3)

        login_button = self.web_driver.find_element(
            By.XPATH, '//*[@id="main"]/div[3]/header/div/div/div[3]/button[2]'
        )
        login_button.click()

        time.sleep(3)

        username = self.web_driver.find_element(
            By.XPATH, '//*[@id="loginModalForm-identity"]'
        )

        email = input("Please provide your e-mail: ")
        username.send_keys(email)

        time.sleep(3)

        my_password = self.web_driver.find_element(
            By.XPATH, '//*[@id="loginModalForm-password"]'
        )
        password = getpass.getpass("Please provide your password: ")
        my_password.send_keys(password)

        time.sleep(3)

        button = self.web_driver.find_element(
            By.XPATH,
            "/html/body/section/div[1]/div/div/div/div[3]/div[2]/ul/li/div/button",
        )
        button.click()

        time.sleep(3)


if __name__ == "__main__":
    driver = webdriver.Chrome()
    driver.get("https://www.pepper.pl")
    scrapper = PepperScrapper(driver=driver)
    scrapper.scan_current_page_for_content()
    scrapper.scan_next_pages(5)
    scrapper.scrapped_data.to_csv("pepper_data.csv")
