# Pepper Scraper Project
This project contains two web scrapers that scrape data from the website pepper.pl. The first scraper is implemented using Selenium, and the second one is implemented using Scrapy. Both scrapers perform the same task: they first visit the main page of the website, scrape URLs for specific items, and save them to a CSV file. Then, they use these URLs to scrape data about the items and save this data to another CSV file.

## Project Structure
The project is structured as follows:

- `pepper_scraper`: This directory contains the Selenium scraper.
- `pepper_scraper/spiders`: This directory contains the Scrapy spiders.
- `pepper_scraper/spiders/pepper_scraper.py`: This is the main Scrapy spider that scrapes the data.
- `pepper_scraper/spiders/pepper_url_spider.py`: This Scrapy spider scrapes the URLs.
- `pepper_scraper/items.py`: This file defines the Scrapy items.
- `pepper_scraper/middlewares.py`: This file contains the Scrapy middlewares.
- `pepper_scraper/pipelines.py`: This file contains the Scrapy pipelines.
- `pepper_scraper/settings.py`: This file contains the Scrapy settings.
- `pepper_scraper/run_spider.py`: This script runs the Scrapy spider.
- `pepper_scraper/scrapy.cfg`: This is the configuration file for Scrapy.
- `pepper_data.csv`: This CSV file contains the scraped URLs.
- `pepper_scrapped_data.csv`: This CSV file contains the scraped data.
- `pepper_data_analysis.ipynb`: This Jupyter notebook contains the data analysis of the scraped data.
- `pepper_recognition.py`: This script processes the scraped data.

## How to Run
### Installation
#### Package
Package management of the project is done using **Poetry** package, which is the state-of-the-art tool for python package management.
To install package go into main project directory and run:  
```poetry install```  

#### Scrapy Splash
We need to download and run scrapy splash server. Easiest way to do it is to use docker image.  
Pull image:  
```docker pull scrapinghub/splash ```  
Run server:  
``` docker run -it -p 8050:8050 --rm scrapinghub/splash```  

### Running selenium scraper
To run the Selenium scraper, navigate to the pepper_scraper directory and run the following command:  
```poetry run python pepper_recognition.py```

### Running Scrapy spiders:
To run the Scrapy spider, navigate to the pepper_scraper directory and run url scraper using the following command:  
```poetry run python -m scrapy crawl pepper_url_spider -o url_scrapy.csv```  

Then, run single item scraper using:  
```poetry run python -m scrapy crawl login_spider -o "data.csv"```  

## Data Analysis
After running the scrapers, you can analyze the scraped data using the ```pepper_data_analysis.ipynb``` Jupyter notebook.  

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing
Contributions are welcome. Please open an issue or submit a pull request.

## Contact
If you have any questions, feel free to contact the project owner.
