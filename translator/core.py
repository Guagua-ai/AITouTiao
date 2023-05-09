import json
import openai
import re
from opencc import OpenCC
from config.translator import TranslatorConfig
from utils.parser import find_first_index
from .rate_limiter import RateLimiter
from .api import create_chat_completion
from .keywords import ai_keywords, non_translatable_terms, title_keys, content_keys

class TranslatorCore(object):
    ''' Translator class '''
    config = None

    def __init__(self, api_key=None):
        assert api_key is not None, 'API key is required'
        openai.api_key = api_key
        self.rate_limiter = RateLimiter(requests_per_minute_limit=200, tokens_per_minute_limit=40000)
        self.config = TranslatorConfig()
        self.version = 2

    def is_related_to_ai(self, text):
        # Check if the text contains any of these AI-related keywords
        for keyword in ai_keywords:
            if keyword.lower() in text.lower():
                return True
        return False
    
    def generate_chinese_news_feed_post(self, author, text):
        if self.version == 1:
            return self.generate_v1(author, text)
        elif self.version == 2:
            return self.generate_v2(author, text)
        else:
            raise Exception("Invalid version number")

    def generate_v1(self, author, text):
        ''' Generate a Chinese news feed post '''
        response = openai.Completion.create(
            engine=self.config.translation_engine,
            prompt=f"你现在是一个新闻记者, 写一篇中文博客关于{author}发布的一篇推文{text}.你给我的结果需要是一个json,里面有两个fields. 第一个field是title,第二个field是content.",
            max_tokens=self.config.translation_max_tokens,
            n=self.config.translation_n,
            stop=None,
            temperature=self.config.translation_temperature,
        )

        news_feed_post = response.choices[0].text.strip()
        print(news_feed_post)
        return self.parse_response(news_feed_post)

    def generate_v2(self, author, text):
        ''' Generate a Chinese news feed post using GPT-4 chat model '''
        messages = [
            {"role": "user", "content": f"你现在是一个新闻记者, 写一篇中文博客关于{author}发布的一篇推文{text}. 你给我的结果需要是一个json,里面有两个fields. 第一个field是title,第二个field是content."}
        ]
        tokens_required = self.config.translation_max_tokens
        self.rate_limiter.rate_limit(tokens_required)

        response = create_chat_completion(
            api_key=openai.api_key,
            model=self.config.translation_model,
            messages=messages
        )

        print(response)
        try:
            news_feed_post = response['choices'][0]['message']['content'].strip()
        except KeyError:
            news_feed_post = response['choices'][0]['text'].strip()
        return self.parse_response(news_feed_post)

    def parse_response(self, response, count=0):
        ''' Parse the response to title and content '''
        if count > 1:
            return None, None
        try:
            response_json = json.loads(response)
            return self.parse(response_json)
        except json.decoder.JSONDecodeError:
            response = self.jsonify(response)
            return self.parse_response(response, count+1)

    def jsonify(self, raw_string):
        ''' Parse the raw string to title and content '''
        title_start_index = find_first_index(
            raw_string, title_keys) + len("：")
        title_end_index = raw_string.find("\n", title_start_index)
        title = raw_string[title_start_index:title_end_index].rstrip(
            ".,!?:;。！？：；").strip()

        content_start_index = find_first_index(
            raw_string, content_keys) + len("：")
        content = raw_string[content_start_index:].strip()

        data = {"title": title, "content": content}
        return json.dumps(data, ensure_ascii=False)

    def parse(self, processed_json):
        ''' Parse the json to title and content '''
        for key in title_keys:
            if key in processed_json:
                title = processed_json[key]
                break
        else:
            title = None

        for key in content_keys:
            if key in processed_json:
                content = processed_json[key]
                break
        else:
            content = None

        return self.clean_title(title), self.clean_content(content)

    def purify_text(self, text):
        ''' Purify the text to simplified Chinese '''
        cc = OpenCC('t2s')  # t2s: Traditional to Simplified
        simplified_text = cc.convert(text)

        # Replace non-translatable terms
        for term in non_translatable_terms:
            simplified_text = simplified_text.replace(
                term, non_translatable_terms[term])

        return simplified_text
    
    def clean_title(self, title):
        ''' Clean the title '''
        title = self.purify_text(title)

        # Define a set of unwanted characters to remove from the beginning and end of the title
        unwanted_chars = ' .,:;!?。：；！？"“”‘’'

        # Remove leading and trailing unwanted characters
        title = title.strip(unwanted_chars)

        return title

    def clean_content(self, content):
        ''' Clean the content '''
        content = self.purify_text(content)

        # Define a regular expression pattern to match unwanted characters at the head and tail
        pattern = r'^[ .,:;!?。：；！？"“”‘’\n]+|[ .,:;!?。：；！？"“”‘’\n]+$'

        # Use re.sub to remove unwanted characters from the head and tail of the content
        cleaned_content = re.sub(pattern, '', content)

        return cleaned_content

