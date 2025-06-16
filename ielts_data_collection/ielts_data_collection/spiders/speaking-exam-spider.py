import scrapy
import re
import os


class SpeakingExamSpider(scrapy.Spider):
    name = 'speaking-exam-spider'
    start_urls = ['https://study4.com/posts/1660/bo-de-du-doan-ielts-speaking-forecast-quy-1-2025-bai-mau-dang-cap-nhat/']

    def parse(self, response):
        tables = response.xpath('//table')
        rows = tables[0].xpath('.//tr')
        data = []
        for row in rows:
            questions = []
            topic = row.xpath('.//span[@style="color:#4a3293"]/strong/text()').get()
            questions_e  = row.xpath('.//span[@style="color:#1a1a1a"]/text()').getall()
            for question in questions_e:
                match = re.match(r"(\d+)\.\s*(.+)", question)
                if match:
                    number = int(match.group(1))
                    question_text = match.group(2)
                    questions.append({
                        "number": number,
                        "question": question_text
                    })
            data.append( {
                "topic": topic,
                "type":1,
                "questionsOne": questions,
                "questionsTwo": "",
                "questionsThree": []
            })
        rows = tables[1].xpath('.//tr')
        for row in rows:
            questions_three = []
            question_two = row.xpath('.//span[@style="color:#4a3293"]/strong/text()').get()
            questions_e  = row.xpath('.//span[@style="color:#1a1a1a"]/text()').getall()
            for question in questions_e:
                match = re.match(r"(\d+)\.\s*(.+)", question)
                if match:
                    number = int(match.group(1))
                    question_text = match.group(2)
                    questions_three.append({
                        "number": number,
                        "question": question_text
                    })
            data.append( {
                "topic": question_two,
                "type":2,
                "questionsOne": [],
                "questionsTwo": question_two,
                "questionsThree": questions_three
            })
        for item in data:
            yield item