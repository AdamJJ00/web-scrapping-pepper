import csv
from pathlib import Path
from ..items import PepperScraperItem
import scrapy
from scrapy_splash import SplashRequest
import re
import os
from loguru import logger


PEPPER_LOGIN = os.getenv("PEPPER_LOGIN")
PEPPER_PASSWORD = os.getenv("PEPPER_PASSWORD")

url_path = Path(__file__).parents[2] / "url_scrapy.csv"


class LoginSpider(scrapy.Spider):
    name = 'login_spider'
    start_urls = ['https://www.pepper.pl/']
    login_url = 'https://www.pepper.pl/login'
    splash_endpoint = 'execute'

    script = """
    function main(splash, args)
        assert(splash:go(args.url))
        assert(splash:wait(1))
        
        splash:set_viewport_full()
        
        local email_input = splash:select('input[name=identity]')   
        email_input:send_text("kuba1302@gmail.com")
        assert(splash:wait(1))
        
        local password_input = splash:select('input[name=password]')   
        password_input:send_text("gpJw6ZGDe3PjDG")
        assert(splash:wait(1))
        
        local button = splash:select('#main > div.flex--expand-v > div.flex--expand-v > div > div > div.js-twoSidesTwins-content.tGrid.width--all-12.box--toW2-b.aGrid.zIndex--atopNormal > div:nth-child(3) > div:nth-child(2) > div > div > ul > li > div > button')
        button:mouse_click()
        splash:wait(1)
        
        return {
            html=splash:html(),
            url = splash:url(),
            cookies = splash:get_cookies(),
            }
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

    def start_requests(self):
        yield SplashRequest(
            url=self.login_url,
            callback=self.after_login,
            endpoint=self.splash_endpoint,
            headers={"User-Agent": " Chrome/58.0.3029.110"},
            args={
                'width': 1000,
                'lua_source': self.script,
                'url': self.login_url,
            }
        )

    def after_login(self, response):
        if response.status == 200:
            logger.info("Login successful")
        else:
            logger.error("Login failed")
        cookies_dict = {cookie['name']: cookie['value'] for cookie in response.data['cookies']}

        print(self.start_urls)
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_page,
                cookies=cookies_dict
            )

    def parse_page(self, response):
        item = PepperScraperItem()
        item["title"] = response.css("span.text--b.size--all-xl.size--fromW3-xxl::text").get(default="title_not_available")

        category_list = response.css("ul.flex.flex--fromW2-wrap.size--all-s.text--lh-1 li::text").getall()
        item["category"] = [element.strip(" \n\t") for element in category_list] if category_list else [
            'category_not_available']

        hottness_extracted = response.css(
            "div.vote-box.overflow--hidden.border.border--color-borderGrey.bRad--a.space--h-1.bRad--circle.flex::text, "
            "div.vote-box.overflow--hidden.border.border--color-borderGrey.bRad--a.space--h-1.bRad--circle.flex.vote-box--muted::text"
        ).get(default="")

        item["hotness"] = re.search(r"\d+", hottness_extracted).group() if hottness_extracted else -1

        item["comments"] = response.css("a[title='Comments']::text").get().strip(" \n\t") if response.css(
            "a[title='Comments']") else -1

        prices = response.css("span.overflow--wrap-off.flex.boxAlign-ai--all-bl")
        item["price_after_discount"] = prices.css("span.threadItemCard-price.text--b.thread-price::text").get(default=-1)
        item["price_before_discount"] = prices.css("span.size--all-xl.size--fromW3-xxl.mute--text.text--lineThrough::text").get(
            default=-1)
        item["percentage_change_in_price"] = prices.css("span.space--ml-2::text").get(default=-1)

        item["place_of_bargain_price"] = response.css("button.text--color-greyShade.overflow--wrap-off span span::text").get(
            default="place_of_bargain_price_not_available")

        return item