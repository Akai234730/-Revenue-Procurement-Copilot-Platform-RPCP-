from app.core.config import get_settings
from app.services.ai_provider import AIProvider, AIProviderError, ProviderRequest, ProviderResult
from app.services.aliyun_qwen_provider import AliyunQwenProvider
from app.services.mock_ai_provider import MockAIProvider


class OpenAIProvider(MockAIProvider):
    provider_name = "openai"

    def execute(self, request: ProviderRequest) -> ProviderResult:
        raise AIProviderError("OpenAI provider not configured yet")


class AzureOpenAIProvider(MockAIProvider):
    provider_name = "azure_openai"

    def execute(self, request: ProviderRequest) -> ProviderResult:
        raise AIProviderError("Azure OpenAI provider not configured yet")


class LocalAIProvider(MockAIProvider):
    provider_name = "local"

    def execute(self, request: ProviderRequest) -> ProviderResult:
        raise AIProviderError("Local AI provider not configured yet")


def get_ai_provider() -> AIProvider:
    settings = get_settings()
    mapping: dict[str, AIProvider] = {
        "mock": MockAIProvider(),
        "openai": OpenAIProvider(),
        "azure_openai": AzureOpenAIProvider(),
        "local": LocalAIProvider(),
        "aliyun_qwen": AliyunQwenProvider(),
    }
    return mapping.get(settings.ai_provider, MockAIProvider())
