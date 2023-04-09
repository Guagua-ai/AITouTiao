import os
import re
import openai
from config.translator import TranslatorConfig

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
    ]

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
        response = openai.Completion.create(
            engine=self.config.translation_engine,
            prompt=f"Image you are Chinese News Feed Reporter, write a Chinese news feed post (capped 200 Chinese words and don't translate author name) for tweet from '{author}': '{text}'",
            max_tokens=self.config.translation_max_tokens,
            n=self.config.translation_n,
            stop=None,
            temperature=self.config.translation_temperature,
        )

        news_feed_post = response.choices[0].text.strip()
        return news_feed_post
