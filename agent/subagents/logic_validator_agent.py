# 逻辑校验助手 — 审查线索链、动机、时间线、信息公平性
from agent.prompts import sub_agents_content

logic_validator_agent = {
    "name": sub_agents_content['logic_validator']['name'],
    "description": sub_agents_content['logic_validator']['description'],
    "system_prompt": sub_agents_content['logic_validator']['system_prompt'],
    "tools": []
}
