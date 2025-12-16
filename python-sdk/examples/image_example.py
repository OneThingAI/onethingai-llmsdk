"""
图片生成示例

演示如何使用 OneThing AI LLM SDK 进行图片生成，支持多种模型和参数配置。
"""

import os
import base64
from datetime import datetime
from pathlib import Path
from onething_llm import OnethingLLM
from onething_llm.types import ImageJobType, ResponseFormat


def save_image_from_url(image_url: str, filename: str) -> str:
    """从URL保存图片（这里只是示例，实际需要requests库）"""
    # 在实际使用中，这里应该使用requests下载图片
    print(f"📷 图片URL: {image_url}")
    print(f"💾 建议保存为: {filename}")
    return filename


def save_image_from_base64(b64_data: str, filename: str) -> str:
    """从base64数据保存图片"""
    try:
        # 解码base64数据
        image_data = base64.b64decode(b64_data)
        
        # 确保输出目录存在
        output_dir = Path("generated_images")
        output_dir.mkdir(exist_ok=True)
        
        # 保存图片
        filepath = output_dir / filename
        with open(filepath, "wb") as f:
            f.write(image_data)
        
        print(f"💾 图片已保存到: {filepath}")
        return str(filepath)
    except Exception as e:
        print(f"❌ 保存图片失败: {e}")
        return filename


def text_to_image_example():
    """文本生成图片示例"""
    # 设置 API 密钥
    api_key = os.environ.get("ONETHING_LLM_API_KEY", "6c5cd6d9f92101f463709726fd2bbebf")
    
    # 创建客户端
    client = OnethingLLM(api_key=api_key)

    print("🎨 文本生成图片示例:")
    print("="*60)
    
    prompts = [
        "一只可爱的橙色猫咪坐在窗台上，背景是夕阳",
        "未来科技城市的夜景，霓虹灯闪烁，飞车穿梭",
        "春天的樱花公园，粉色花瓣飘落，情侣在散步"
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n📝 提示词 {i}: {prompt}")
        
        try:
            # 生成图片
            response = client.images.generate(
                model="gemini-3-pro-image",  # 使用指定的模型
                prompt=prompt,
                job_type=ImageJobType.GENERATION,
                n=1,  # 生成1张图片
                width=1024,
                height=1024,
                response_format=ResponseFormat.URL,  # 先用URL格式
            )
            
            print(f"✅ 生成成功！")
            print(f"状态: {response.status}")
            print(f"任务ID: {response.job_id}")
            print(f"进度: {response.progress}%")
            
            # 使用新的results属性获取图片结果
            results = response.results
            if results and len(results) > 0:
                print(f"生成的图片数量: {len(results)}")
                for j, result in enumerate(results):
                    if result.url:
                        filename = f"text2img_{i}_{j+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        save_image_from_url(result.url, filename)
                    elif result.b64_json:
                        filename = f"text2img_{i}_{j+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        save_image_from_base64(result.b64_json, filename)
        
        except Exception as e:
            print(f"❌ 生成失败: {e}")
    
    return client


def image_edit_example(client):
    """图片编辑示例"""
    print("\n🎭 图片编辑示例:")
    print("="*60)
    
    # 注意：这里需要准备一张输入图片
    input_image_path = "input_image.png"  # 你需要提供一张图片
    
    if not Path(input_image_path).exists():
        print(f"⚠️  输入图片不存在: {input_image_path}")
        print("请准备一张图片放在当前目录下，命名为 input_image.png")
        return
    
    try:
        # 读取输入图片并转为base64（简化示例）
        with open(input_image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode()
        
        # 带dataurl前缀
        input_images = [{
            "b64_json": 'data:image/png;base64,' + image_data,
        }]
        
        edit_prompt = "给这张图片添加彩虹效果"
        print(f"📝 编辑提示: {edit_prompt}")
        
        # 编辑图片
        response = client.images.edit(
            model="gemini-3-pro-image",
            prompt=edit_prompt,
            input_images=input_images,
            n=1,
            response_format=ResponseFormat.URL,
            height=1024,
            width=1024
        )
        
        print(f"✅ 编辑成功！")
        print(f"状态: {response.status}")
        print(f"任务ID: {response.job_id}")
        
        results = response.results
        if results and len(results) > 0:
            for j, result in enumerate(results):
                if result.url:
                    filename = f"edited_{j+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    save_image_from_url(result.url, filename)
    
    except Exception as e:
        print(f"❌ 编辑失败: {e}")


def main():
    """主函数"""
    print("🖼️  OneThing AI LLM SDK - Gemini 3 Pro Image 图片生成示例集合")
    print("="*80)
    
    try:
        # 基础文本生成图片
        client = text_to_image_example()
        
        # 图片编辑示例
        image_edit_example(client)
        
        # 关闭客户端
        client.close()
        print("\n✅ 图片生成示例运行完成！")
        print("📁 生成的图片保存在 generated_images/ 目录中")
        
    except Exception as e:
        print(f"❌ 程序错误: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")


if __name__ == "__main__":
    main()