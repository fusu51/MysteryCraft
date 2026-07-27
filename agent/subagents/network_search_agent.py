# 素材搜集助手 — 负责搜索历史背景、真实案件、场景氛围素材
from agent.prompts import sub_agents_content
from tools.tavily_tool import internet_search


network_search_agent = {
    "name": sub_agents_content['material']['name'],
    "description": sub_agents_content['material']['description'],
    "system_prompt": sub_agents_content['material']['system_prompt'],
    "tools": [internet_search]
}
