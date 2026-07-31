import os
from dotenv import load_dotenv, find_dotenv
from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI

load_dotenv(find_dotenv())


def _create_chat_model(base_url_key, api_key_key, model_key):
    """创建一个 ChatOpenAI 实例，支持 max_retries 和超时"""
    base_url = os.getenv(base_url_key)
    api_key = os.getenv(api_key_key)
    model_name = os.getenv(model_key)

    if not base_url or not api_key or not model_name:
        return None

    return ChatOpenAI(
        model=model_name,
        openai_api_key=api_key,
        openai_api_base=base_url,
        max_retries=2,
        request_timeout=120,
    )


# 主模型
primary = _create_chat_model("OPENAI_BASE_URL", "OPENAI_API_KEY", "MODEL_NAME")

# 备用模型
fallback = _create_chat_model("FALLBACK_BASE_URL", "FALLBACK_API_KEY", "FALLBACK_MODEL")


class ModelWithFallback:
    """主模型连续失败 n 次后自动切换备用"""

    def __init__(self, primary_model, fallback_model):
        self._primary = primary_model
        self._fallback = fallback_model
        self._failures = 0
        self._max_failures = 3

    @property
    def active(self):
        if self._failures >= self._max_failures and self._fallback:
            return self._fallback
        return self._primary

    def report_failure(self):
        self._failures += 1

    def report_success(self):
        self._failures = 0

    # 代理所有属性到 active 模型
    def __getattr__(self, name):
        return getattr(self.active, name)


if fallback:
    model = ModelWithFallback(primary, fallback)
else:
    model = primary
