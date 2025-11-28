import json
import logging
from typing import List, Dict, Any
from langchain_qwq import ChatQwen
from config import get_settings
from models import KeywordList
from prompts import PromptTemplates


logger = logging.getLogger(__name__)


class LLMService:
    """大模型服务封装"""

    def __init__(self):
        """初始化LLM服务"""
        settings = get_settings()

        # 初始化ChatQwen客户端
        self.llm = ChatQwen(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            model=settings.llm_model
        )

    def get_professional_explanation(self, title: str) -> str:
        """
        获取专业问题分析

        Args:
            title: 需要分析的问题类型或标题

        Returns:
            str: 专业分析和概要
        """
        try:
            # 使用LangChain ChatPromptTemplate
            prompt_template = PromptTemplates.get_explanation_prompt()
            prompt = prompt_template.invoke({"title": title})

            response = self.llm.invoke(prompt)
            return response.content.strip()

        except Exception as e:
            logger.error(f"获取专业分析失败: {e}")
            raise Exception(f"大模型调用失败: {str(e)}")

    def extract_keywords(self, title: str) -> List[str]:
        """
        提取相关关键词

        Args:
            title: 输入标题

        Returns:
            List[str]: 关键词列表
        """
        try:
            # 使用LangChain ChatPromptTemplate
            prompt_template = PromptTemplates.get_keyword_extraction_prompt()
            prompt = prompt_template.invoke({"title": title})

            # 定义JSON schema
            json_schema = KeywordList.model_json_schema()

            # 使用guided_json进行结构化输出
            response = self.llm.invoke(prompt, extra_body={"guided_json": json_schema})
            response_text = response.content

            # 解析JSON响应
            try:
                keyword_data = json.loads(response_text)
                keyword_obj = KeywordList(**keyword_data)
                return keyword_obj.keywords
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {e}, 响应内容: {response_text}")
                raise Exception("关键词提取结果格式错误")

        except Exception as e:
            logger.error(f"关键词提取失败: {e}")
            raise Exception(f"关键词提取失败: {str(e)}")

    def generate_analysis_report(self, title: str, requests_data: List[Dict[str, Any]]) -> str:
        """
        生成分析报告

        Args:
            title: 分析类别标题
            requests_data: 诉求数据列表

        Returns:
            str: 分析报告内容
        """
        try:
            # 限制数据量，最多2000条
            limited_data = requests_data[:2000]

            # 格式化诉求数据
            analysis_str = self._format_requests_for_analysis(limited_data)

            # 使用LangChain ChatPromptTemplate
            prompt_template = PromptTemplates.get_analysis_report_prompt()
            prompt = prompt_template.invoke({
                "title": title,
                "analysis_str": analysis_str
            })

            # 输出提示词前100行到控制台
            prompt_str = str(prompt)
            lines = prompt_str.split('\n')
            first_100_lines = '\n'.join(lines[:100])
            print("=" * 50)
            print("分析报告提示词前100行:")
            print("=" * 50)
            print(first_100_lines)
            print("=" * 50)
            if len(lines) > 100:
                print(f"(提示词总共{len(lines)}行，仅显示前100行)")
            print("=" * 50)

            # 调用大模型生成报告
            response = self.llm.invoke(prompt)

            return response.content.strip()

        except Exception as e:
            logger.error(f"生成分析报告失败: {e}")
            raise Exception(f"分析报告生成失败: {str(e)}")

    def _format_requests_for_analysis(self, requests_data: List[Dict[str, Any]]) -> str:
        """
        格式化诉求数据用于分析

        Args:
            requests_data: 诉求数据列表

        Returns:
            str: 格式化的诉求内容字符串
        """
        formatted_requests = []

        for req in requests_data:
            # 截取内容，最多100字
            content = req.get('content', '')
            if len(content) > 100:
                content = content[:100]

            # 格式化单条诉求
            formatted_req = f"""诉求编号: {req.get('serial_number', 'N/A')}
标题: {req.get('title', 'N/A')}
内容: {content}
时间: {req.get('time', 'N/A')}
---"""

            formatted_requests.append(formatted_req)

        return '\n'.join(formatted_requests)


# 全局LLM服务实例
_llm_service = None


def get_llm_service() -> LLMService:
    """获取LLM服务实例（单例模式）"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service