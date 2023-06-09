import getpass
import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup as BS
from bs4.element import Tag
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class PepperLinksScrapper:
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
        return ["link"]

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
        link = self.extract_title(content_div)
        return [link]

    @staticmethod
    def extract_title(bargain_div: Tag) -> str:
        title_anchor = bargain_div.find(
            "strong", {"class": "thread-title"}
        ).find("a")
        return title_anchor["href"]

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


class PepperScrapper:
    def __init__(self, links_file, driver: webdriver):
        self.web_driver = driver
        self.links_file = links_file
        self.data = pd.read_csv(links_file)

    def scrape_additional_data(self):
        additional_info = []
        for link in self.data["link"]:
            time.sleep(0.2)
            self.web_driver.get(link)
            info = self.scrape_single_link()
            additional_info.append(info)
        additional_data = pd.DataFrame(additional_info)
        self.data = pd.concat([self.data, additional_data], axis=1)

    def scrape_single_link(self):
        response = self.web_driver.page_source
        soup = BS(response, "html.parser")

        try:
            title = soup.find("span", {"class": "text--b size--all-xl size--fromW3-xxl"}).get_text()
        except AttributeError:
            title = "title_not_available"

        try:
            list_category = soup.find("ul", {"class": "flex flex--fromW2-wrap size--all-s text--lh-1"}).find_all('li')
            category = [element.get_text().strip(" \n\t") for element in list_category]
        except AttributeError:
            category = ['category_not_available']

        try:
            hottness_tag = soup.find(
                "div",
                {
                    "class": "vote-box overflow--hidden border border--color-borderGrey bRad--a space--h-1 bRad--circle flex"
                },
            )
            if hottness_tag:
                hottness_extracted = hottness_tag.get_text()
            else:
                hottness_tag = soup.find(
                    "div",
                    {
                        "class": "vote-box overflow--hidden border border--color-borderGrey bRad--a space--h-1 bRad--circle flex vote-box--muted"
                    },
                )
                hottness_extracted = hottness_tag.get_text()
            try:
                hottness = re.search(r"\d+", hottness_extracted).group()
            except AttributeError:
                hottness = -1
        except AttributeError:
            hottness = -1

        try:
            number_of_comments =  soup.find("a", {"title": "Comments"}).get_text().strip(" \n\t")
        except AttributeError:
            number_of_comments = -1


        try:
            prices = soup.find("span", {"class": "overflow--wrap-off flex boxAlign-ai--all-bl"})
            try:
                price_after_discount = prices.find(
                    "span",
                    {"class": "threadItemCard-price text--b thread-price"},
                ).get_text()
            except AttributeError:
                price_after_discount = -1

            try:
                prices_and_percentage = prices.find("span", {"class": "flex--inline boxAlign-ai--all-c"})
                price_before_discount = prices_and_percentage.find(
                    "span",
                    {"class": "size--all-xl size--fromW3-xxl mute--text text--lineThrough"}).get_text()
            except AttributeError:
                price_before_discount = -1

            try:
                prices_and_percentage = prices.find("span", {"class": "flex--inline boxAlign-ai--all-c"})
                percentage_change_in_price = prices_and_percentage.find("span", {"class": "space--ml-2"}).get_text()
            except AttributeError:
                percentage_change_in_price = -1

        except AttributeError:
            price_before_discount = -1
            price_after_discount = -1
            percentage_change_in_price = -1

        try:
            place_of_bargain_price = soup.find("button", {"class": "text--color-greyShade overflow--wrap-off"}).span.span.get_text()
        except AttributeError:
            place_of_bargain_price = "place_of_bargain_price_not_available"

        info = {
            'title': title,
            'category': category,
            'hottness': hottness,
            'number_of_comments': number_of_comments,
            'price_after_discount': price_after_discount,
            'price_before_discount': price_before_discount,
            'percentage_change_in_price': percentage_change_in_price,
            'place_of_bargain_price': place_of_bargain_price
        }
        return info

    def save_data(self, output_file):
        self.data.to_csv(output_file, index=False)


if __name__ == "__main__":
    driver = webdriver.Chrome()
    driver.get("https://www.pepper.pl")
    scrapper = PepperLinksScrapper(driver=driver)
    scrapper.scan_current_page_for_content()
    scrapper.scan_next_pages(5)
    scrapper.scrapped_data.reset_index(drop=True, inplace=True)
    scrapper.scrapped_data.to_csv("pepper_links.csv")
    links_file = "pepper_links.csv"
    output_file = "pepper_data.csv"
    pepper_scrapper = PepperScrapper(links_file, driver)
    pepper_scrapper.scrape_additional_data()
    pepper_scrapper.save_data(output_file)
    time.sleep(2)
    driver.quit()