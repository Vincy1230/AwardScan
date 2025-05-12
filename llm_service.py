from dotenv import load_dotenv
from pydantic import SecretStr
from models.awardInfo import AwardInfo
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
import os


load_dotenv()
OPENAI_API_KEY = SecretStr(os.getenv("OPENAI_API_KEY", ""))
BASE_URL = os.getenv("BASE_URL", default="https://api.deepseek.com")
MODEL_NAME = os.getenv("MODEL_NAME", default="deepseek-chat")


def extract_award_info(markdown_text: str) -> dict:
    """
    从 Markdown 文本中提取获奖信息

    Args:
        markdown_text (str): Markdown 格式的文本内容

    Returns:
        dict: 提取的获奖信息字典
    """
    # 初始化 LLM
    llm = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model=MODEL_NAME,
        base_url=BASE_URL
    )

    # 创建输出解析器
    parser = PydanticOutputParser(pydantic_object=AwardInfo)

    # 创建提示模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个专业的获奖信息提取助手。请从给定的文本中提取获奖相关信息。
        请严格按照以下格式提取信息：
        {format_instructions}
        
        如果某项信息在文本中未找到，请将其设置为空字符串 `\"\"`。"""),
        ("user", "{text}")
    ])

    # 构建完整提示
    chain = prompt | llm | parser

    # 执行提取
    try:
        result = chain.invoke({
            "text": markdown_text,
            "format_instructions": parser.get_format_instructions()
        })
        return result.model_dump()
    except Exception as e:
        print(f"提取过程中发生错误: {str(e)}")
        return {}
