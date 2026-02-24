"""LLM 客户端单元测试"""
import pytest
from core import LLMFactory, BaseLLMClient, LLMResponse, Message


class TestLLMFactory:
    """LLM 工厂测试"""

    def test_register_client(self):
        """测试注册客户端"""
        class TestClient(BaseLLMClient):
            def chat(self, messages, **kwargs):
                return LLMResponse(content="test", model="test", usage={}, raw_response={})
            def stream_chat(self, messages, **kwargs):
                yield "test"

        LLMFactory.register("test_provider", TestClient)
        assert "test_provider" in LLMFactory.get_providers()

    def test_get_providers(self):
        """测试获取所有已注册的提供商"""
        providers = LLMFactory.get_providers()
        assert isinstance(providers, list)
        # 应该包含默认的提供商
        assert "openai" in providers or "deepseek" in providers


class TestLLMResponse:
    """LLM 响应数据类测试"""

    def test_response_creation(self):
        """测试创建响应对象"""
        response = LLMResponse(
            content="Hello",
            model="gpt-4",
            usage={"prompt_tokens": 10, "completion_tokens": 5},
            raw_response={"id": "test123"}
        )
        assert response.content == "Hello"
        assert response.model == "gpt-4"
        assert response.usage["prompt_tokens"] == 10

    def test_response_with_finish_reason(self):
        """测试包含 finish_reason 的响应"""
        response = LLMResponse(
            content="Done",
            model="test",
            usage={},
            raw_response={},
            finish_reason="stop"
        )
        assert response.finish_reason == "stop"


class TestMessage:
    """消息数据类测试"""

    def test_message_creation(self):
        """测试创建消息"""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_message_to_dict(self):
        """测试转换为字典"""
        msg = Message(role="system", content="You are a helper")
        data = msg.to_dict()
        assert data == {"role": "system", "content": "You are a helper"}

    def test_message_from_dict(self):
        """测试从字典创建"""
        data = {"role": "user", "content": "Hello"}
        msg = Message.from_dict(data)
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_message_user_factory(self):
        """测试用户消息工厂方法"""
        msg = Message.user("Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_message_assistant_factory(self):
        """测试助手消息工厂方法"""
        msg = Message.assistant("Hi there")
        assert msg.role == "assistant"
        assert msg.content == "Hi there"

    def test_message_system_factory(self):
        """测试系统消息工厂方法"""
        msg = Message.system("You are a helpful assistant")
        assert msg.role == "system"
        assert msg.content == "You are a helpful assistant"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
