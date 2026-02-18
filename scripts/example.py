"""快速示例脚本"""
from core import LLMFactory
from config import KeyManager
from scenarios import PropertyChatbotService


def main():
    # 1. 查看可用的Provider
    print("Available providers:", KeyManager.get_available_providers())

    # 2. 直接使用LLM
    try:
        llm = LLMFactory.create("deepseek", "deepseek-chat")
        response = llm.chat([
            {"role": "user", "content": "你好，请介绍一下你自己"}
        ])
        print("\n=== LLM Response ===")
        print(response.content)
    except Exception as e:
        print(f"LLM Error: {e}")

    # 3. 使用智能客服场景
    print("\n=== Property Chatbot ===")
    try:
        chatbot = PropertyChatbotService()
        result = chatbot.chat("你好，我想查询一下物业费怎么缴")
        print(result.get("message", result.get("error")))
    except Exception as e:
        print(f"Chatbot Error: {e}")


if __name__ == "__main__":
    main()
