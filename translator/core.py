import json
import openai
from opencc import OpenCC
from config.translator import TranslatorConfig
from utils.parser import find_first_index


class TranslatorCore(object):
    ''' Translator class '''
    config = None
    ai_keywords = [
        "AI", "artificial intelligence", "GPT", "OpenAI", "machine learning", "deep learning", "neural network",
        "natural language processing", "NLP", "computer vision", "reinforcement learning", "supervised learning",
        "unsupervised learning", "transfer learning", "generative model", "chatbot", "robotics", "automation",
        "algorithm", "data science", "big data", "predictive analytics", "GAN", "generative adversarial network",
        "convolutional neural network", "CNN", "RNN", "recurrent neural network", "transformer", "BERT", "language model",
        "image recognition", "object detection", "semantic segmentation", "self-driving car", "autonomous vehicle",
        "virtual assistant", "Siri", "Alexa", "Google Assistant", "Cortana", "TensorFlow", "Keras", "PyTorch", "MXNet",
        "scikit-learn", "data mining", "feature extraction", "dimensionality reduction", "PCA", "t-SNE",
        "gradient descent", "backpropagation", "optimization", "loss function", "activation function", "ReLU",
        "sigmoid", "tanh", "softmax", "dropout", "regularization", "overfitting", "underfitting", "bias-variance tradeoff",
        "cross-validation", "hyperparameter tuning", "grid search", "random search", "Bayesian optimization",
        "ensemble learning", "bagging", "boosting", "stacking", "decision tree", "random forest", "XGBoost",
        "LightGBM", "CatBoost", "SVM", "support vector machine", "k-means", "clustering", "dbscan", "hierarchical clustering",
        "classification", "regression", "time series", "anomaly detection", "recommendation system", "collaborative filtering",
        "content-based filtering", "sentiment analysis", "topic modeling", "LDA", "word2vec", "GloVe", "fastText",
        "word embedding", "pre-trained model", "pre-trained language model", "pre-trained transformer", "pre-trained BERT",
        "google", "facebook", "amazon", "microsoft", "apple", "ibm", "alibaba", "baidu", "tencent", "huawei",
        "intel", "nvidia", "tesla", "uber", "airbnb", "netflix", "twitter", "reddit", "youtube", "instagram",
    ]
    title_keys = ['title', 'Title', 'TITLE', '标题',
                  '题目', '摘要', '概要', '標題', '標題名稱', '標題名字']
    content_keys = ['content', 'Content', 'CONTENT', '内容',
                    '正文', '正文内容', '正文摘要', '正文概要', '內容', '內容摘要', '內容概要']

    non_translatable_terms = {
        "深度思维": "DeepMind",
        "斯玛·阿尔特曼": "Sam Altman",
        "斯玛·阿尔特曼": "Sam Altman",
        "安德烈·卡帕斯基": "Andrej Karpathy",
        "聊天GPT": "ChatGPT",
    }

    def __init__(self, api_key=None):
        assert api_key is not None, 'API key is required'
        openai.api_key = api_key
        self.config = TranslatorConfig()

    def translate_to_chinese(self, text):
        response = openai.Completion.create(
            engine=self.config.translation_engine,
            prompt=f"Translate the following English text to Simplified Chinese: '{text}'",
            max_tokens=self.config.translation_max_tokens,
            n=self.config.translation_n,
            stop=None,
            temperature=self.config.translation_temperature,
        )

        translation = response.choices[0].text.strip()
        return translation

    def is_related_to_ai(self, text):
        # Check if the text contains any of these AI-related keywords
        for keyword in self.ai_keywords:
            if keyword.lower() in text.lower():
                return True
        return False

    def generate_chinese_news_feed_post(self, author, text):
        ''' Generate a Chinese news feed post '''
        response = openai.Completion.create(
            engine=self.config.translation_engine,
            prompt=f"Image you are Chinese News Feed Reporter, write a Chinese news feed post (capped under 600 Chinese characters, remove all urls and don't translate human names) for tweet from '{author}': '{text}' Response must be a json with two fields. First field is title and second field is content.",
            max_tokens=self.config.translation_max_tokens,
            n=self.config.translation_n,
            stop=None,
            temperature=self.config.translation_temperature,
        )

        news_feed_post = response.choices[0].text.strip()
        print(news_feed_post)
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
            raw_string, self.title_keys) + len("：")
        title_end_index = raw_string.find("\n", title_start_index)
        title = raw_string[title_start_index:title_end_index].rstrip(
            ".,!?:;。！？：；").strip()

        content_start_index = find_first_index(
            raw_string, self.content_keys) + len("：")
        content = raw_string[content_start_index:].strip()

        data = {"title": title, "content": content}
        return json.dumps(data, ensure_ascii=False)

    def parse(self, processed_json):
        ''' Parse the json to title and content '''
        for key in self.title_keys:
            if key in processed_json:
                title = processed_json[key]
                break
        else:
            title = None

        for key in self.content_keys:
            if key in processed_json:
                content = processed_json[key]
                break
        else:
            content = None

        return self.purify_text(title), self.purify_text(content)

    def purify_text(self, text):
        ''' Purify the text to simplified Chinese '''
        cc = OpenCC('t2s')  # t2s: Traditional to Simplified
        simplified_text = cc.convert(text)

        # Replace non-translatable terms
        for term in self.non_translatable_terms:
            simplified_text = simplified_text.replace(
                term, self.non_translatable_terms[term])

        return simplified_text
