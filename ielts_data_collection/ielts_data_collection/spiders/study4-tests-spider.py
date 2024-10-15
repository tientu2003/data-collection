

import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from dotenv import load_dotenv
import os

import re


load_dotenv()

class Study4TestsSpider(scrapy.Spider):
    name = "study4-tests"

    start_urls = []
    for i in range(1,70):
        start_urls.append(f"https://study4.com/my-account/tests/?page={i}")

    def parse(self, response):
        divs = response.xpath('//div[@class="user-test"]')
        for div in divs:
            if re.search("writing",div.xpath('.//h2[@class="h5"]/text()').get(),re.IGNORECASE):
                continue
            elif re.search("reading",div.xpath('.//h2[@class="h5"]/text()').get(),re.IGNORECASE):
                continue
            elif re.search("listening",div.xpath('.//h2[@class="h5"]/text()').get(),re.IGNORECASE):
                continue
            else:
                link = div.xpath(".//a[@href][1]/@href").get()
                yield {
                    'url': link
                }


