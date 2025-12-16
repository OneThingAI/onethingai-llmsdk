"""
视频生成示例

演示如何使用 OneThing AI LLM SDK 进行文本生成视频。
注意：视频生成仅支持异步请求，会返回任务ID，需要后续轮询查询结果。
"""

import os
from onething_llm import OnethingLLM


def main():
    """主函数"""
    print("🎬 OneThing AI LLM SDK - 文生视频示例")
    print("="*60)
    
    # 设置 API 密钥
    api_key = os.environ.get("ONETHING_LLM_API_KEY", "6c5cd6d9f92101f463709726fd2bbebf")
    
    # 创建客户端
    client = OnethingLLM(api_key=api_key)
    
    # 视频生成提示词
    prompt = "一只橙色的小猫在花园里追蝴蝶，阳光明媚，花朵盛开"
    print(f"📝 提示词: {prompt}\n")
    
    try:
        # 生成视频（异步请求）
        response = client.videos.text_to_video(
            model="sora-2",
            prompt=prompt,
            width=1024,
            height=576,
            duration=5,
            fps=24
        )
        
        print(f"✅ 任务提交成功！")
        print(f"📋 任务ID: {response.data}")
        print(f"📊 状态: {response.data.status}")
        print(f"⏳ 进度: {response.data.progress}%")
        print(f"\n💡 提示: 视频生成是异步操作，请保存任务ID并稍后查询结果")
        
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
    finally:
        client.close()


if __name__ == "__main__":
    main()