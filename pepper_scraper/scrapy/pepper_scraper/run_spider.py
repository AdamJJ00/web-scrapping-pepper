import pandas as pd
from scrapy.crawler import CrawlerProcess

from pepper_scraper.pepper_scraper.spiders.pepper_url_spider import (
    PepperSpider,
)


def run_scraper():
    scrapped_data = pd.DataFrame(columns=PepperSpider.field_names)

    process = CrawlerProcess(
        {
            "USER_AGENT": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "LOG_LEVEL": "INFO",
            "DOWNLOAD_DELAY": 1,
        }
    )
    process.crawl(PepperSpider)
    process.start()

    scrapped_data = pd.DataFrame(PepperSpider.results)
    scrapped_data.to_csv("pepper_scrapped_data.csv", index=False)


if __name__ == "__main__":
    run_scraper()
