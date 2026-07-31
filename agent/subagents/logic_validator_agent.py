from agent.prompts import sub_agents_content
from tools.upload_file_read_tool import read_file_content

logic_validator_agent = {
    "name": sub_agents_content['logic_validator']['name'],
    "description": sub_agents_content['logic_validator']['description'],
    "system_prompt": sub_agents_content['logic_validator']['system_prompt'],
    "tools": [read_file_content]
}
