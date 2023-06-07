import csv
import os
import re
from pathlib import Path

import scrapy
from loguru import logger
from scrapy_splash import SplashRequest

from ..items import PepperScraperItem
from bs4 import BeautifulSoup

PEPPER_LOGIN = os.getenv("PEPPER_LOGIN")
PEPPER_PASSWORD = os.getenv("PEPPER_PASSWORD")

url_path = Path(__file__).parents[2] / "url_scrapy.csv"


class LoginSpider(scrapy.Spider):
    name = "login_spider"
    start_urls = ["https://www.pepper.pl/"]
    login_url = "https://www.pepper.pl/login"
    splash_endpoint = "execute"

    script = f"""
    function main(splash, args)
        assert(splash:go(args.url))
        assert(splash:wait(1))
        
        splash:set_viewport_full()
        
        local email_input = splash:select('input[name=identity]')   
        email_input:send_text("{PEPPER_LOGIN}")
        assert(splash:wait(1))
        
        local password_input = splash:select('input[name=password]')   
        password_input:send_text("{PEPPER_PASSWORD}")
        assert(splash:wait(1))
        
        local button = splash:select('#main > div.flex--expand-v > div.flex--expand-v > div > div > div.js-twoSidesTwins-content.tGrid.width--all-12.box--toW2-b.aGrid.zIndex--atopNormal > div:nth-child(3) > div:nth-child(2) > div > div > ul > li > div > button')
        button:mouse_click()
        splash:wait(1)
        
        return {{
            html=splash:html(),
            url = splash:url(),
            cookies = splash:get_cookies(),
            }}
    end
    """

    def __init__(self, *args, **kwargs):
        self.load_csv()
        super().__init__(*args, **kwargs)

    def load_csv(self):
        with open(str(url_path), "r") as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            self.start_urls = [row[0] for row in reader]
            self.start_urls = self.start_urls

    def start_requests(self):
        yield SplashRequest(
            url=self.login_url,
            callback=self.after_login,
            endpoint=self.splash_endpoint,
            args={
                "width": 1000,
                "lua_source": self.script,
                "url": self.login_url,
            },
        )

    def after_login(self, response):
        if response.status == 200:
            logger.info("Login successful")
        else:
            logger.error("Login failed")

        cookies_dict = {
            cookie["name"]: cookie["value"]
            for cookie in response.data["cookies"]
        }
        for url in self.start_urls:
            yield scrapy.Request(
                url=url, callback=self.parse_page, cookies=cookies_dict
            )

    def parse_page(self, response):

        item = PepperScraperItem()
        item["title"] = response.css(
            "span.text--b.size--all-xl.size--fromW3-xxl::text"
        ).get(default="title_not_available")

        soup = BeautifulSoup(response.body, "html.parser")

        try:
            list_category = soup.find("ul", {"class": "flex flex--fromW2-wrap size--all-s text--lh-1"}).find_all('li')
            category = [element.get_text().strip(" \n\t") for element in list_category]
        except AttributeError:
            category = ['category_not_available']
        item["category"] = category

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

        item["hotness"] = hottness
        item["comments"] = (
            response.css("a[title='Comments']::text").get().strip(" \n\t")
            if response.css("a[title='Comments']")
            else -1
        )

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
        item["price_before_discount"] = price_before_discount
        item["price_after_discount"] = price_after_discount
        item["percentage_change_in_price"] = percentage_change_in_price
        item["place_of_bargain_price"] = place_of_bargain_price
        yield item
