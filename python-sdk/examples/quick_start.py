"""
快速开始示例

最简单的 OneThing AI LLM SDK 使用示例。
"""

import os
from onething_llm import OnethingLLM


def main():
    # 设置 API 密钥
    api_key = os.environ.get("ONETHING_LLM_API_KEY", "your-api-key")
    
    # 创建客户端
    client = OnethingLLM(api_key=api_key)

    print("🚀 OneThing AI LLM SDK 快速开始\n")    # 文本生成
    print("💬 聊天对话:")
    try:
        # 使用自定义文本接口
        response = client.text.chat(
            model="gpt-4o",
            messages=[{"role": "user", "content": "你好，介绍一下自己"}]
        )
        print(f"回复: {response}")
    except Exception as e:
        print(f"错误: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # OpenAI 兼容接口
    print("🔗 OpenAI 兼容接口:")
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "什么是人工智能？"}]
        )
        print(f"回复: {response.choices[0].message.content}")
    except Exception as e:
        print(f"错误: {e}")
    
    # 关闭客户端
    client.close()
    print("\n✅ 示例运行完成！")


if __name__ == "__main__":
    main()