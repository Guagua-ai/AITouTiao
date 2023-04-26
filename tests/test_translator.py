from app import app
from translator.core import TranslatorCore


class TestTranslatorCore:
    def test_core_parseResponse_withNewLine(self):
        # Test the parser
        core = TranslatorCore(api_key='dummy')
        assert core.parse_response(response="""
        标题：安德烈·卡尔帕蒂的AI研究 
        内容：安德烈·卡尔帕蒂发布了一项AI研究报告，介绍了两个令牌0/1和上下文长度为3的baby GPT，并以有限状态马尔科夫链的形式来观察它。该模型以“111101111011110”序列训练了50次，参数和Transformer架构改变了箭头上的概率。
        """) == (
            "安德烈·卡尔帕蒂的AI研究",
            "安德烈·卡尔帕蒂发布了一项AI研究报告，介绍了两个令牌0/1和上下文长度为3的baby GPT，并以有限状态马尔科夫链的形式来观察它。该模型以“111101111011110”序列训练了50次，参数和Transformer架构改变了箭头上的概率。",
        )

    def test_core_parseResponse_nonTranslableTerms(self):
        # Test the parser
        core = TranslatorCore(api_key='dummy')
        assert core.parse_response(response="""
        标题：深度思维发布新工作
        内容：深度思维宣布发布新的工作，由WeidingerLaura、EmpiricallyKev、saffronhuang、reverettai、MartinJChadwick、summerfieldlab、IasonGabriel、Tina Zhu和Richard Everett共同完成。这项新的工作深度思维将为人工智能开发提供重要的支持，使技术在更短的时间内取得更大的进展。
        """) == (
            "DeepMind发布新工作",
            "DeepMind宣布发布新的工作，由WeidingerLaura、EmpiricallyKev、saffronhuang、reverettai、MartinJChadwick、summerfieldlab、IasonGabriel、Tina Zhu和Richard Everett共同完成。这项新的工作DeepMind将为人工智能开发提供重要的支持，使技术在更短的时间内取得更大的进展。",
        )

    def test_core_purifyText_nonTranslableTerms(self):
        core = TranslatorCore(api_key='dummy')
        assert core.purify_text(
            text="深度思维宣布发布新的工作，由WeidingerLaura、EmpiricallyKev、saffronhuang、reverettai、MartinJChadwick、summerfieldlab、IasonGabriel、Tina Zhu和Richard Everett共同完成。这项新的工作深度思维将为人工智能开发提供重要的支持，使技术在更短的时间内取得更大的进展。") == (
            "DeepMind宣布发布新的工作，由WeidingerLaura、EmpiricallyKev、saffronhuang、reverettai、MartinJChadwick、summerfieldlab、IasonGabriel、Tina Zhu和Richard Everett共同完成。这项新的工作DeepMind将为人工智能开发提供重要的支持，使技术在更短的时间内取得更大的进展。"
        )
