import scrapy

from ..items import PepperScraperUrl

MAX_PAGE_NUMBER = 5


class PepperUrlSpider(scrapy.Spider):
    name = "pepper_url_spider"
    start_urls = ["https://www.pepper.pl/?page=1"]
    field_names = [
        "link",
    ]
    results = []

    def parse(self, response):
        # Extracting data from the current page
        for article in response.css("article"):
            info = PepperScraperUrl()
            link = article.css("strong.thread-title a").attrib["href"]
            info["link"] = link
            yield info

        # Following the pagination link
        current_page = response.url.split("=")[-1]
        if current_page.isdigit():
            current_page = int(current_page)
            if current_page < MAX_PAGE_NUMBER:
                next_page = f"https://www.pepper.pl/?page={current_page+1}"
                yield scrapy.Request(next_page, callback=self.parse)
