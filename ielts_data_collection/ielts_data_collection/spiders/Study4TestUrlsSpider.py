import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from dotenv import load_dotenv
import os

load_dotenv()

class Study4TestUrlsSpider(scrapy.Spider):
    name = "study4testurls"

    def __init__(self):

        # Sử dụng Selenium để đăng nhập
        options = webdriver.ChromeOptions()

        options.add_argument("--headless")  # Mở trình duyệt ở chế độ headless

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.get("https://study4.com/login/")

        self.driver.find_element(By.CLASS_NAME,"f-login-button").click()

        email_input = self.driver.find_element(By.ID,"email")
        email_input.send_keys(os.getenv("my-account"))

        password_input = self.driver.find_element(By.ID,"pass")
        password_input.send_keys(os.getenv("my-password"))

        self.driver.find_element(By.ID,"loginbutton").click()

        time.sleep(3)

        self.driver.find_element(By.XPATH,"//div[@role='button']").click()

        time.sleep(5)


    def start_requests(self):
        # FETCH ALL TEST URLS
        for index in range(1,30):
            self.driver.get(f"https://study4.com/tests/ielts/?page={index}")
            response = scrapy.http.HtmlResponse(
                url=self.driver.current_url,
                body=self.driver.page_source,
                encoding='utf-8')
            for item in self.get_all_test_urls(response):
                yield item  # Trả về từng kết quả để Scrapy xử lý

    def get_all_test_urls(self,response):
        test_items = response.xpath('//div[@class="testitem-wrapper "]')
        for test_item in test_items:
            link = test_item.xpath('.//a[@class="text-dark"][1]/@href').get()
            if link:
                # Sử dụng Scrapy Request để tiếp tục crawl URL
                yield scrapy.Request(
                    url=response.urljoin(link),  # Đảm bảo URL đầy đủ
                    callback=self.parse_test_page  # Hàm xử lý sau khi truy cập URL
                )
    def parse_test_page(self, response):
        # Xử lý dữ liệu từ trang đích sau khi vào được từng URL test
        # Ví dụ: Lưu URL trang test hoặc trích xuất thêm dữ liệu
        self.log(f"Scraped test page: {response.url}")
        yield {
            "test_url": response.url
            # Các dữ liệu khác nếu có
        }

    def __del__(self):
        self.driver.quit()