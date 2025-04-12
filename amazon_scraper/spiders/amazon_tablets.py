from scrapy_selenium import SeleniumRequest
import scrapy
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class AmazonTabletsSpider(scrapy.Spider):
    name = "amazon_tablets"
    allowed_domains = ["amazon.com"]
    page_limit = 20  # Scrape up to 20 pages

    def start_requests(self):
        url = "https://www.amazon.com/s?k=tablet&crid=3RFXCHF6VT84L&sprefix=%2Caps%2C275&ref=nb_sb_ss_recent_1_0_recent"
        yield SeleniumRequest(
            url=url,
            callback=self.parse,
            wait_time=5,
            screenshot=False,
            dont_filter=True
        )

    def parse(self, response):
        self.logger.info(f"Scraping URL: {response.url}")
        driver = response.meta['driver']

        products = response.xpath('//div[contains(@class, "s-main-slot")]/div')
        for product in products:
            title = product.xpath('.//h2[contains(@class, "a-size-medium")]/span/text()').get()
            price = product.xpath('.//span[contains(@class, "a-price-whole")]/text()').get()
            url = product.xpath('.//a[@class="a-link-normal"]/@href').get()
            ratings = product.xpath('.//span[contains(@class, "a-icon-alt")]/text()').get()

            if title:
                yield {
                    'title': title.strip(),
                    'price': price.strip() if price else 'Not Available',
                    'url': response.urljoin(url) if url else 'No URL',
                    'ratings': ratings.strip() if ratings else 'No Ratings'
                }

        # Handle pagination
        current_page = self.extract_current_page(driver.current_url)
        if current_page < self.page_limit:
            try:
                next_button = driver.find_elements(By.XPATH, '//a[contains(@class, "s-pagination-next")]')
                if next_button:
                    self.logger.info(f"Proceeding to page {current_page + 1}...")
                    next_button[0].click()

                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "s-main-slot")]'))
                    )

                    yield SeleniumRequest(
                        url=driver.current_url,
                        callback=self.parse,
                        wait_time=5,
                        dont_filter=True
                    )
                else:
                    self.logger.info("No next button found. Stopping crawl.")
            except Exception as e:
                self.logger.error(f"Pagination error: {e}")
        else:
            self.logger.info("Reached page limit. Stopping crawl.")

    @staticmethod
    def extract_current_page(url):
        """Extract the current page number from the URL."""
        if 'page=' in url:
            try:
                return int(url.split('page=')[1].split('&')[0])
            except (ValueError, IndexError):
                return 1
        return 1


