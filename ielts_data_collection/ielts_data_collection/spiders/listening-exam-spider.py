import json
from fnmatch import translate

import scrapy


class ListeningExam:
    def __init__(self, test_name, recordings):
        self.test_name = test_name
        self.recordings = recordings

    def to_dict(self):
        return {
            "test_name": self.test_name,
            "recordings": [recording.to_dict() for recording in self.recordings]
        }
class Recording:
    def __init__(self, audio_url, transcript ,question_groups):
        self.audio_url = audio_url
        self.transcript = transcript
        self.question_groups = question_groups

    def to_dict(self):
        return {
            "audio_url": self.audio_url,
            "transcript" : self.transcript,
            "question_groups": [question_group.to_dict() for question_group in self.question_groups]
        }

class QuestionGroup:
    def __init__(self, context, questions, question_type , context_table):
        self.context = context
        self.context_table = context_table
        self.questions = questions
        self.question_type = question_type
    def to_dict(self):
        return {
            "context":self.context,
            "context_table":self.context_table,
            "type":self.question_type,
            "questions": [question.to_dict() for question in self.questions]
        }

class Question:
    def __init__(self, question_number,question_text,answer_options ,answer):
        self.question_number = question_number
        self.answer_options = answer_options
        self.question_text = question_text
        self.answer = answer

    def to_dict(self):
        return {
            "question_number": self.question_number,
            "question_text": self.question_text,
            "answer_options": self.answer_options,
            "answer": self.answer
        }

class ListeningExamSpider(scrapy.Spider):
    name = "study4-lis-exam"
    start_urls = []

    base_url = "https://study4.com"
    with open("list-tests.json","r") as lis:
        data = json.load(lis)

    for row in data:
        start_urls.append(base_url + row['url'] + "details")

    def parse(self,response):
        test_name = response.xpath('//h1[@class="h3 text-center"]/text()').get()
        test_name = test_name.replace("Đáp án chi tiết: ","")
        test_name = test_name.replace("\n","").strip()

        recording_data = []

        recording_sessions =  response.xpath('//div[@class="test-questions-wrapper"]')

        for recording_session in recording_sessions:
            context_audio = recording_session.xpath('.//div[@class="context-content context-audio"]')
            audio_source = context_audio.xpath('.//source[@src]/@src').get()
            transcript_ps = recording_session.xpath('.//div[@class="collapse"]//p/text()').getall()
            transcript_data = []
            for transcript_p in transcript_ps:
                transcript_p = transcript_p.replace(" ","")
                transcript_data.append(transcript_p)

            question_groups_data = []
            question_group_wrappers = recording_session.xpath('.//div[@class="question-group-wrapper"]')

            for q_group_wrapper in question_group_wrappers:
                context =  q_group_wrapper.xpath('.//div[@class="context-content text-highlightable"]')
                context_datas = []
                context_table = []
                questions_data = []

                p_elements_in_context = context.xpath('.//p')
                for p_element in p_elements_in_context:
                    data = p_element.xpath('string(.)').get()

                    # Loại bỏ các ký tự không mong muốn nếu cần
                    if data:
                        data = data.replace(" ", "").strip()  # Loại bỏ ký tự khoảng trắng không ngắt (nbsp) và trim
                        context_datas.append(data)


                is_table = context.xpath(".//table").get() is not None
                is_choice_question = q_group_wrapper.xpath('.//div[@class="questions-wrapper two-cols"]').get() is not None

                if is_table:
                    question_type = "table"
                    rows = context.xpath(".//table/tbody/tr")
                    question_part = q_group_wrapper.xpath('.//div[@class="question-twocols-right"]')

                    for row in rows:
                        columns = row.xpath(".//td")
                        column_data = [col.xpath(".//text()").getall() for col in columns]
                        column_data_cleaned = [" ".join(data).strip() for data in column_data]
                        context_table.append(column_data_cleaned)
                    question_answer_elements  = question_part.xpath('.//div[@class="question-wrapper"]')
                    for qa_element in question_answer_elements:
                        question_number = qa_element.xpath('string(.//div[@class="question-number"])').get()
                        question_number =  question_number.replace("\n","").strip()
                        answer = qa_element.xpath('string(.//div[@class="mt-2 text-success"])').get()
                        answer = answer.replace("Đáp án đúng:","")
                        answer = answer.replace("\n","").strip()
                        questions_data.append(Question(question_number=question_number,question_text="null",answer=answer, answer_options="null"))
                else:
                    if is_choice_question:
                        question_type = "choice"
                        question_options = q_group_wrapper.xpath('.//div[@class="questions-wrapper two-cols"]//div[@class="question-wrapper"]')
                        for question_option in question_options:
                            question_options_data = []
                            question_number = question_option.xpath('string(.//div[@class="question-number"])').get()
                            question_number =  question_number.replace("\n","").strip()
                            answer_options = question_option.xpath(".//label[@class='form-check-label']/text()").getall()

                            for answer_option in answer_options:
                                answer_option =  answer_option.replace("\n","").strip()
                                question_options_data.append(answer_option)
                            question_context = question_option.xpath('string(.//div[@class="question-text "])').get()
                            question_context = question_context.replace("\n","").strip()
                            answer = question_option.xpath('string(.//div[@class="mt-2 text-success"])').get()
                            answer = answer.replace("Đáp án đúng:","")
                            answer = answer.replace("\n","").strip()

                            questions_data.append(Question(question_number=question_number,question_text=question_context,answer_options=question_options_data, answer=answer))
                    else:
                        question_type = "normal"
                        question_answer_elements = q_group_wrapper.xpath('.//div[@class="question-wrapper"]')

                        for qa_element in question_answer_elements:
                            question_context = qa_element.xpath('string(.//div[@class="question-text "])').get()
                            question_context = question_context.replace("\n","").strip()

                            question_number = qa_element.xpath('string(.//div[@class="question-number"])').get()
                            question_number =  question_number.replace("\n","").strip()

                            answer = qa_element.xpath('string(.//div[@class="mt-2 text-success"])').get()
                            answer = answer.replace("Đáp án đúng:","")
                            answer = answer.replace("\n","").strip()

                            questions_data.append(Question(question_number=question_number,question_text=question_context,answer=answer, answer_options="null"))

                question_groups_data.append(QuestionGroup(context=context_datas,question_type=question_type,questions=questions_data, context_table=context_table))

            recording_data.append(Recording(audio_url=audio_source,transcript=transcript_data,question_groups= question_groups_data))

        yield ListeningExam(test_name=test_name,recordings=recording_data).to_dict()

