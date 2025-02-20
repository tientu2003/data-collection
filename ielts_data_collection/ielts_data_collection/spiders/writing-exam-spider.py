import json
from fnmatch import translate

import scrapy


class WritingExam:
    def __init__(self, context, task, diagram_url):
        self.context = context
        self.task = task
        self.diagram_url = diagram_url

    def to_dict(self):
        return {
            "context": self.context,
            "task": self.task,
            "diagram_url": self.diagram_url
        }

class WritingExamSpider(scrapy.Spider):
    name = "study4-writing-exam"
    start_urls = []

    base_url = "https://study4.com"
    with open("writing-tests.json","r") as lis:
        data = json.load(lis)

    for row in data:
        start_urls.append(base_url + row['url'] + "details")

    def parse(self,response):

        test_content =  response.xpath('//div[@id="test-content"]')

        tests =  test_content.xpath('.//div[@class="question-twocols-left"]')

        for test in tests:
            context = " ".join(test.xpath('.//span//text() | .//strong//text() | .//p//text() | .//div//text()').getall())
            context = context.replace(" ","").replace("\n","").strip()
            is_task1 =  test.xpath('.//img[@src]').get() is not None
            if is_task1:
                url = test.xpath('.//img[@src]/@src').get()
                yield WritingExam(context=context, task=1, diagram_url=url).to_dict()
            else:
                yield WritingExam(context=context, task=2, diagram_url=None).to_dict()


