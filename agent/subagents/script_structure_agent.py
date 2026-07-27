# 剧本结构助手 —— 查询角色原型库、诡计模式库、模板库、剧情框架库
from agent.prompts import sub_agents_content
from tools.script_db_tools import (
    search_character_archetypes,
    search_trick_patterns,
    search_script_templates,
    search_plot_patterns
)


script_structure_agent = {
    "name": sub_agents_content['script_structure']['name'],
    "description": sub_agents_content['script_structure']['description'],
    "system_prompt": sub_agents_content['script_structure']['system_prompt'],
    "tools": [
        search_character_archetypes,
        search_trick_patterns,
        search_script_templates,
        search_plot_patterns
    ]
}
