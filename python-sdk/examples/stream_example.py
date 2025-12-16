"""
流式对话示例

演示如何使用 OneThing AI LLM SDK 进行流式对话，实时接收响应。
"""

import os
import json
from onething_llm import OnethingLLM


def parse_stream_line(line: str) -> dict:
    """解析流式数据行"""
    line = line.strip()
    
    # 跳过空行和注释
    if not line or line.startswith(":"):
        return {}
    
    # 解析 SSE 格式: "data: {...}"
    if line.startswith("data: "):
        data_str = line[6:]  # 去掉 "data: " 前缀
        
        # 检查结束标志
        if data_str.strip() == "[DONE]":
            return {"done": True}
        
        try:
            return json.loads(data_str)
        except json.JSONDecodeError:
            return {}
    
    return {}


def extract_content_from_stream_data(data: dict) -> str:
    """从流式数据中提取内容"""
    # 检查标准格式
    if "choices" in data and len(data["choices"]) > 0:
        choice = data["choices"][0]
        
        # OpenAI 兼容格式
        if "delta" in choice and "content" in choice["delta"]:
            return choice["delta"]["content"] or ""
        
        # 文本完成格式
        if "text" in choice:
            return choice["text"] or ""
    
    # 检查直接内容格式
    if "content" in data:
        return data["content"] or ""
    
    if "text" in data:
        return data["text"] or ""
    
    # 检查自定义格式
    if "data" in data and isinstance(data["data"], dict):
        inner_data = data["data"]
        if "content" in inner_data:
            return inner_data["content"] or ""
        if "text" in inner_data:
            return inner_data["text"] or ""
    
    return ""


def stream_chat_example():
    """流式聊天示例"""
    # 设置 API 密钥
    api_key = os.environ.get("ONETHING_LLM_API_KEY", "your-api-key")
    
    # 创建客户端
    client = OnethingLLM(api_key=api_key)
    
    print(" 流式聊天对话:")
    print("问题: 请详细介绍一下人工智能的发展历史")
    print("回复: ", end="", flush=True)
    
    try:
        # 使用流式接口
        stream = client.text.chat(
            model="gpt-4o",
            messages=[{
                "role": "user", 
                "content": "请详细介绍一下人工智能的发展历史"
            }],
            stream=True,
            max_tokens=500,
            temperature=0.7
        )
        
        complete_response = ""
        chunk_count = 0
        
        for line in stream:
            if isinstance(line, str):
                data = parse_stream_line(line)
                
                # 检查是否结束
                if data.get("done"):
                    break
                
                # 提取内容
                content = extract_content_from_stream_data(data)
                if content:
                    print(content, end="", flush=True)
                    complete_response += content
                    chunk_count += 1
        
        print("\n")
        print(f"\n✅ 完整回复: {len(complete_response)} 字符，{chunk_count} 个数据块")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
    
    print("\n" + "="*60 + "\n")
    return client


def stream_completion_example(client):
    """流式文本完成示例"""
    print("📝 流式文本完成:")
    print("提示: 写一首关于春天的诗")
    print("回复: ", end="", flush=True)
    
    try:
        # 使用流式完成接口
        stream = client.text.completions(
            model="gpt-4o",
            prompt="写一首关于春天的诗，要求有韵律感，表达生机勃勃的景象：",
            stream=True,
            max_tokens=200,
            temperature=0.8
        )
        
        complete_response = ""
        chunk_count = 0
        
        for line in stream:
            if isinstance(line, str):
                data = parse_stream_line(line)
                
                # 检查是否结束
                if data.get("done"):
                    break
                
                # 提取内容
                content = extract_content_from_stream_data(data)
                if content:
                    print(content, end="", flush=True)
                    complete_response += content
                    chunk_count += 1
        
        print("\n")
        print(f"\n✅ 完整回复: {len(complete_response)} 字符，{chunk_count} 个数据块")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")


def interactive_stream_chat(client):
    """交互式流式聊天"""
    print("🤖 交互式流式聊天 (输入 'quit' 退出):")
    print("-" * 60)
    
    while True:
        try:
            user_input = input("\n👤 你: ").strip()
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("👋 再见！")
                break
            
            if not user_input:
                continue
            
            print("🤖 AI: ", end="", flush=True)
            
            stream = client.text.chat(
                model="gpt-4o",
                messages=[{"role": "user", "content": user_input}],
                stream=True,
                max_tokens=300,
                temperature=0.7
            )
            
            complete_response = ""
            
            for line in stream:
                if isinstance(line, str):
                    data = parse_stream_line(line)
                    
                    if data.get("done"):
                        break
                    
                    content = extract_content_from_stream_data(data)
                    if content:
                        print(content, end="", flush=True)
                        complete_response += content
            
            print()  # 换行
            
        except KeyboardInterrupt:
            print("\n\n👋 收到中断信号，退出聊天...")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")


def main():
    """主函数"""
    print("🌊 OneThing AI LLM SDK 流式请求示例集合\n")
    
    try:
        # 运行流式聊天示例
        client = stream_chat_example()
        
        # 运行流式文本完成示例
        stream_completion_example(client)
        
        # 询问是否要进行交互式聊天
        print("\n" + "="*60)
        choice = input("是否要进行交互式流式聊天？(y/n): ").strip().lower()
        if choice in ['y', 'yes', '是']:
            interactive_stream_chat(client)
        
        # 关闭客户端
        client.close()
        print("\n✅ 流式示例运行完成！")
        
    except Exception as e:
        print(f"❌ 程序错误: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")


if __name__ == "__main__":
    main()