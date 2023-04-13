from app import app
from translator.core import TranslatorCore


class TestTranslatorCore:
    def test_core_parse_withNewLine(self):
        # Test the parser
        core = TranslatorCore(api_key='dummy')
        assert core.parse_response(response="""
        标题：安德烈·卡尔帕蒂的AI研究 
        内容：安德烈·卡尔帕蒂发布了一项AI研究报告，介绍了两个令牌0/1和上下文长度为3的baby GPT，并以有限状态马尔科夫链的形式来观察它。该模型以“111101111011110”序列训练了50次，参数和Transformer架构改变了箭头上的概率。
        """) == (
            "安德烈·卡尔帕蒂的AI研究",
            "安德烈·卡尔帕蒂发布了一项AI研究报告，介绍了两个令牌0/1和上下文长度为3的baby GPT，并以有限状态马尔科夫链的形式来观察它。该模型以“111101111011110”序列训练了50次，参数和Transformer架构改变了箭头上的概率。",
        )

    def test_core_parse_withoutNewLine(self):
        core = TranslatorCore(api_key='dummy')
        assert core.parse_response("""{"title": "最新的图像生成技术发展！", "content": "5年前，我们为了把CIFAR-10 32x32尺寸的“图像”训练成最先进的结果而感到自豪！可以看出轮子形状、汽车/飞机零件、有机结构和纹理，太酷了！"}""") == (
            "最新的图像生成技术发展！",
            "5年前，我们为了把CIFAR-10 32x32尺寸的“图像”训练成最先进的结果而感到自豪！可以看出轮子形状、汽车/飞机零件、有机结构和纹理，太酷了！",
        )
