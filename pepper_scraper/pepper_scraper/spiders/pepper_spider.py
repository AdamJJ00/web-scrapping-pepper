import scrapy
import re

class PepperScraperItem(scrapy.Item):
    title= scrapy.Field()
    price_before_discount= scrapy.Field()
    price_after_discount= scrapy.Field()
    hotness = scrapy.Field()
    comments = scrapy.Field()
    username = scrapy.Field()
    link = scrapy.Field()


class PepperSpider(scrapy.Spider):
    name = "pepper_spider"
    start_urls = ["https://www.pepper.pl/"]
    field_names = [
        "title",
        "price_before_discount",
        "price_after_discount",
        "hotness",
        "comments",
        "username",
        "link",
    ]
    results = []

    def parse(self, response):
        # Extracting data from the current page
        for article in response.css("article"):
            info = PepperScraperItem()
            title, link = self.extract_title(article)
            hotness = self.extract_hotness(article)
            price_before_discount, price_after_discount = self.extract_prices(article)
            username = self.extract_username(article)

            info["title"] = title
            info["link"] = link
            info["hotness"] = hotness
            info["price_before_discount"] = price_before_discount
            info["price_after_discount"] = price_after_discount
            info["username"] = username
            print(title)
            yield info

        # Following the pagination link
        next_page = response.css("a.buttonNext::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    @staticmethod
    def extract_title(article):
        title_anchor = article.css("strong.thread-title a")
        title = title_anchor.attrib["title"]
        link = title_anchor.attrib["href"]
        return title, link

    @staticmethod
    def extract_hotness(article):
        hotness_tag = article.css(
            "div.cept-vote-box.vote-box.overflow--hidden.border.border--color-borderGrey.bRad--a.thread-noClick"
        )
        if hotness_tag:
            hotness_extracted = hotness_tag.css("::text").get()
        else:
            hotness_tag = article.css(
                "div.vote-box.vote-box--muted.space--h-2.border.border--color-borderGrey.bRad--a.text--color-grey.space--mr-3"
            )
            hotness_extracted = hotness_tag.css("::text").get()

        hotness = re.search(r"\d+", hotness_extracted)
        if hotness:
            return hotness.group()
        else:
            return "-1"

    @staticmethod
    def extract_username(article):
        return article.css("span.thread-username::text").get().strip()

    @staticmethod
    def extract_prices(article):
        prices = article.css("span.overflow--fade")
        price_after_discount = prices.css("span.overflow--wrap-off::text").get(
            default="price not available"
        )
        price_before_discount_tag = prices.css(
            "span.flex--inline.boxAlign-ai--all-c.space--ml-2"
        ).css("span")
        price_before_discount = price_before_discount_tag.css("::text").get(
            default="price not available"
        )
        return price_before_discount, price_after_discount


