import json
from gc import callbacks

import scrapy

class IeltsReadingTest:
    def __init__(self, test_name, passages):
        self.test_name = test_name
        self.passages = passages

    def to_dict(self):
        return {
            "test_name": self.test_name,
            "passages": [passage.to_dict() for passage in self.passages]
        }


class Passage:
    def __init__(self , title , paragraphs, question_groups):
        self.title = title
        self.paragraphs = paragraphs
        self.question_groups = question_groups

    def to_dict(self):
        return {
            "article_title": self.title,
            "article_context": [paragraph.to_dict() for paragraph in self.paragraphs],
            "question_groups": [group.to_dict() for group in self.question_groups]
        }

class Paragraph:
    def __init__(self, title_p, content):
        self.title_p = title_p
        self.content = content

    def to_dict(self):
        return {
            "letter": self.title_p,
            "paragraph": self.content
        }

reading_question_types = {
    1:'Matching Headings',
    2:'Matching Paragraph Information',
    3:'Matching Features',
    4:'Matching Sentence Endings',
    5:'True False Not Given or Yes No Not Given',
    6:'Multiple Choice',
    7:'List of Options',
    8:'Choose a Title',
    9:'Short Answers',
    10:'Sentence Completion',
    11:'Summary Completion',
    12:'Table Completion',
    13:'Flow Chart Completion',
    14:'Completion Diagrams',
}

class QuestionGroup:
    def __init__(self,questions, questions_type, contexts):
        self.contexts = contexts
        self.questions_type = questions_type
        self.questions = questions

    def to_dict(self):
        return {
            "context":[context.to_dict() for context in self.contexts],
            "questions_type": self.questions_type,
            "questions": [question.to_dict() for question in self.questions]
        }

class ContextData:
    def __init__(self, data):
        self.data = data

    def to_dict(self):
        return {
            "data": self.data
        }

class Question:
    def __init__(self, question_number ,question_text, answer):
        self.question_number = question_number
        self.question_text = question_text
        self.answer = answer

    def to_dict(self):
        return {
            "question_number": self.question_number,
            "question_text": self.question_text,
            "answer": self.answer
        }


class ReadingTestSpider(scrapy.Spider):
    name = "study4-read-tests"

    start_urls = []

    base_url = "https://study4.com"

    with open("read-tests.json","r") as lis:
        data = json.load(lis)

    # index = 0

    for row in data:
        # if index == 0:
        start_urls.append(base_url + row['url'] + "details")
        # index = 1

    def parse(self,response):
        # reading test name
        test_name = response.xpath('//h1[@class="h3 text-center"]/text()').get()
        test_name = test_name.replace("Đáp án chi tiết: ","")

        # to store 3 passages in this tests
        passage_data = []

        passages_e =  response.xpath('//div[@class="test-questions-wrapper"]')

        for passage_e in passages_e:

            #get context of passage
            article = passage_e.xpath('.//div[@class="question-twocols-left"]')

            #get name of passage
            title =  article.xpath('string(.//h2)').get()

            #get all paragraphs appears in article
            p_elements = article.xpath('.//p')

            paragraphs = []
            flag = 2
            temp = "null"
            for p in p_elements:
                datas =  p.xpath('string(.//span)').get()

                if flag == 2:
                    flag = 0
                    continue
                # Filter unexpected data
                if datas == "" or " " in datas:
                    continue
                elif len(datas) == 1 or len(datas) == 2:
                    temp = datas
                    flag = 1

                # add paragraph with "name corresponding to paragraph"
                elif flag == 1:
                    paragraphs.append(Paragraph(title_p=temp,content=datas))
                    flag = 0
                else:
                    paragraphs.append(Paragraph(title_p="null",content=datas))

            question_groups = []
            question_part = passage_e.xpath('.//div[@class="question-twocols-right"]')

            ques_group_wrappers = question_part.xpath('.//div[@class="question-group-wrapper"]')

            for qg_wrapper in ques_group_wrappers:

                p_elements_in_context =  qg_wrapper.xpath('.//div[@class="context-content text-highlightable"]//p')

                context_datas = []
                for p_element in p_elements_in_context:
                    data = p_element.xpath("string(.//span)").get()
                    data = data.replace(" ","")
                    context_datas.append(ContextData(data=data))

                questions_data = []
                question_answer_elements  = qg_wrapper.xpath('.//div[@class="question-wrapper"]')
                for qa_element in question_answer_elements:
                    question_number = qa_element.xpath('string(.//div[@class="question-number"])').get()
                    question_number =  question_number.replace("\n","")
                    question_context = qa_element.xpath('string(.//div[@class="question-text "])').get()
                    question_context = question_context.replace("\n","")

                    answer = qa_element.xpath('string(.//div[@class="mt-2 text-success"])').get()

                    answer = answer.replace("Đáp án đúng:","")
                    answer = answer.replace("\n","")
                    if question_context:
                        questions_data.append(Question(question_number=question_number,question_text=question_context,answer=answer))
                    else:
                        questions_data.append(Question(question_number=question_number,question_text="null",answer=answer))

                question_groups.append(QuestionGroup(contexts=context_datas,questions_type="unknown" ,questions=questions_data))
            passage_data.append(Passage(title = title, paragraphs= paragraphs, question_groups= question_groups))

        yield IeltsReadingTest(test_name=test_name, passages= passage_data).to_dict()

            
