import json

import scrapy


class AudioSaveSpider(scrapy.Spider):
    name = "audio-url"
    start_urls = []

    base_url = "https://study4.com"
    with open("list-tests.json","r") as lis:
        data = json.load(lis)

    for row in data:
        start_urls.append(base_url + row['url'] + "details")

    def parse(self,response):

        recording_sessions =  response.xpath('//div[@class="test-questions-wrapper"]')

        for recording_session in recording_sessions:
            context_audio = recording_session.xpath('.//div[@class="context-content context-audio"]')
            audio_source = context_audio.xpath('.//source[@src]/@src').get()
            yield {"url":audio_source}