# 定义一个网络搜索的工具！
# ======================== 导入核心依赖 ========================
# 类型注解：增强代码提示和静态检查能力
from typing import Literal
# LangChain 工具装饰器：将普通函数转为 Agent 可调用的工具
from langchain_core.tools import tool
# Tavily 官方客户端：实现网络搜索核心功能
from tavily import TavilyClient

# 系统/第三方依赖
import os  # 系统路径/环境变量处理
from dotenv import load_dotenv  # 加载 .env 文件中的环境变量

# 自定义模块：工具调用埋点监控（需确保 api 模块可导入）
from api.monitor import monitor

# ======================== 初始化配置 ========================
# 加载项目根目录的 .env 文件，读取环境变量（如 TAVILY_API_KEY）
load_dotenv()


# 步骤1： 定义一个TavilyClient对象
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


# 步骤2： 定义一个网络搜索工具
@tool
def internet_search(
        query: str,
        topic: Literal["news",  "finance",  "general"] = "general",
        max_results: int = 5,
        include_raw_content: bool = False
):
    """
    根据用户问题进行网络信息搜索。

    剧本杀创作时建议的搜索维度：
    1. 时代背景细节 — 搜索服饰/建筑/交通/饮食/社会规则等，如 "1930年代上海法租界街景建筑风格"
    2. 真实案件素材 — 搜索历史上真实犯罪案例，如 "民国时期著名谋杀案 犯罪手法"
    3. 场景氛围描写 — 搜索特定场景的感官细节，如 "民国上海法租界梧桐树下 光影 气味"

    注意：主要用于搜索公开的网络信息，数据库查询或内部知识库检索请用其他工具。

    :param query: 用户的查询信息
    :param topic: 查询类型 (news/finance/general)
    :param max_results: 返回的最大条数
    :param include_raw_content: 是否返回原始内容（False=精简, True=详细）
    :return: 搜索结果
    """
    # 每次调用工具，都都会向前端推进调用进度！
    # 参数1： 工具的名字  参数2： 就是调用工具的参数信息
    monitor.report_tool(tool_name="网络搜索工具",
                        args={"query": query, "topic": topic, "max_results": max_results,
                              "include_raw_content": include_raw_content})

    return tavily_client.search(query=query, topic=topic,
                                max_results=max_results, include_raw_content=include_raw_content)
