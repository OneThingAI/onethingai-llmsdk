"""
视频生成示例

演示如何使用 OneThing AI SDK 进行视频生成，包括文生视频和图生视频功能。
"""

import os
import base64
import time
from datetime import datetime
from pathlib import Path
from onethingai import OnethingAI
from onethingai.types import VideoJobType, SyncMode


def save_video_from_url(video_url: str, filename: str) -> str:
    """从URL保存视频（这里只是示例，实际需要requests库）"""
    # 在实际使用中，这里应该使用requests下载视频
    print(f"🎬 视频URL: {video_url}")
    print(f"💾 建议保存为: {filename}")
    return filename


def check_video_status(client, job_id: str) -> dict:
    """检查视频生成状态"""
    try:
        response = client.videos.get_job_status(job_id)
        return {
            "status": response.data.status,
            "progress": response.data.progress,
            "job_id": job_id,
            "response": response
        }
    except Exception as e:
        print(f"❌ 检查状态失败: {e}")
        return {"status": "error", "error": str(e)}


def text_to_video_example():
    """文生视频示例"""
    # 设置 API 密钥
    api_key = os.environ.get("ONETHINGAI_API_KEY", "your-api-key")
    
    # 创建客户端
    client = OnethingAI(api_key=api_key)
    
    print("🎬 文生视频示例:")
    print("="*60)
    
    prompts = [
        "一只橙色的小猫在花园里追蝴蝶，阳光明媚，花朵盛开",
        "未来城市的交通，飞行汽车在摩天大楼间穿梭，霓虹闪烁",
        "海浪拍打着沙滩，夕阳西下，海鸥在天空中飞翔"
    ]
    
    job_ids = []
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n📝 提示词 {i}: {prompt}")
        
        try:
            # 异步生成视频
            response = client.videos.text_to_video(
                model="sora-2",  # 使用指定的视频模型
                prompt=prompt,
                sync_mode=SyncMode.ASYNC,  # 异步模式
                width=1024,
                height=576,
                duration=5,  # 5秒视频
                fps=24,
                audio_enabled=False,
                seed=42
            )
            
            print(f"✅ 任务提交成功！")
            print(f"📋 任务ID: {response.data.job_id}")
            print(f"📊 状态: {response.data.status}")
            
            job_ids.append({
                "job_id": response.data.job_id,
                "prompt": prompt,
                "index": i
            })
            
        except Exception as e:
            print(f"❌ 生成失败: {e}")
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
    
    return client, job_ids


def image_to_video_example(client):
    """图生视频示例"""
    print("\n🖼️➡️🎬 图生视频示例:")
    print("="*60)
    
    # 检查是否有输入图片
    input_image_path = "input_image.png"
    
    if not Path(input_image_path).exists():
        print(f"⚠️ 输入图片不存在: {input_image_path}")
        print("请准备一张图片放在当前目录下，命名为 input_image.png")
        return []
    
    try:
        # 读取输入图片并转为base64
        with open(input_image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode()
        
        input_images = [{
            "url": None,
            "b64_json": 'data:image/png;base64,' + image_data
        }]
        
        video_prompt = "让这张图片中的场景动起来，添加自然的动画效果"
        print(f"📝 视频提示: {video_prompt}")
        
        # 图生视频
        response = client.videos.image_to_video(
            model="sora-2",
            prompt=video_prompt,
            input_images=input_images,
            sync_mode=SyncMode.ASYNC,
            width=1024,
            height=576,
            duration=3,  # 3秒视频
            fps=24
        )
        
        print(f"✅ 图生视频任务提交成功！")
        print(f"📋 任务ID: {response.data.job_id}")
        print(f"📊 状态: {response.data.status}")
        
        return [{
            "job_id": response.data.job_id,
            "prompt": video_prompt,
            "type": "image_to_video"
        }]
        
    except Exception as e:
        print(f"❌ 图生视频失败: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        return []


def poll_video_jobs(client, job_ids: list):
    """轮询视频生成任务状态"""
    print("\n⏳ 开始轮询任务状态...")
    print("="*60)
    
    pending_jobs = job_ids.copy()
    completed_jobs = []
    
    max_attempts = 30  # 最大轮询次数
    attempt = 0
    
    while pending_jobs and attempt < max_attempts:
        attempt += 1
        print(f"\n🔄 轮询第 {attempt} 次 (剩余任务: {len(pending_jobs)})")
        
        for job in pending_jobs.copy():
            job_id = job["job_id"]
            job_type = job.get("type", "text_to_video")
            
            try:
                status_info = check_video_status(client, job_id)
                
                if status_info["status"] == "success":
                    print(f"✅ 任务 {job_id[:8]}... 完成!")
                    
                    # 处理完成的任务
                    response = status_info["response"]
                    if response.data.result and response.data.result.data:
                        for i, video_result in enumerate(response.data.result.data):
                            if hasattr(video_result, 'url') and video_result.url:
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                filename = f"{job_type}_{job.get('index', 'unknown')}_{i+1}_{timestamp}.mp4"
                                save_video_from_url(video_result.url, filename)
                    
                    completed_jobs.append(job)
                    pending_jobs.remove(job)
                    
                elif status_info["status"] == "failed":
                    print(f"❌ 任务 {job_id[:8]}... 失败!")
                    if "error" in status_info:
                        print(f"   错误: {status_info['error']}")
                    
                    completed_jobs.append(job)
                    pending_jobs.remove(job)
                    
                elif status_info["status"] == "processing":
                    progress = status_info.get("progress", 0)
                    print(f"🔄 任务 {job_id[:8]}... 进行中 ({progress:.1f}%)")
                    
                else:
                    print(f"🤔 任务 {job_id[:8]}... 状态未知: {status_info['status']}")
                
            except Exception as e:
                print(f"❌ 检查任务 {job_id[:8]}... 失败: {e}")
        
        if pending_jobs:
            print(f"⏸️ 等待 10 秒后继续...")
            time.sleep(10)
    
    # 结果总结
    print(f"\n📊 轮询结果总结:")
    print(f"✅ 完成任务: {len(completed_jobs)}")
    print(f"⏳ 剩余任务: {len(pending_jobs)}")
    
    if pending_jobs:
        print("\n⚠️ 以下任务未完成:")
        for job in pending_jobs:
            print(f"  - {job['job_id'][:8]}... ({job.get('prompt', 'Unknown')[:30]}...)")


def sync_video_example(client):
    """同步视频生成示例（如果支持）"""
    print("\n⚡ 同步视频生成示例:")
    print("="*60)
    
    simple_prompt = "一朵花在微风中轻柔摆动"
    print(f"📝 提示词: {simple_prompt}")
    
    try:
        # 尝试同步生成（可能不被支持）
        response = client.videos.text_to_video(
            model="sora-2",
            prompt=simple_prompt,
            sync_mode=SyncMode.SYNC,  # 同步模式
            width=512,
            height=512,
            duration=2,  # 短视频
            fps=24
        )
        
        print(f"✅ 同步生成完成！")
        print(f"📊 状态: {response.data.status}")
        
        if response.data.result and response.data.result.data:
            for i, video_result in enumerate(response.data.result.data):
                if hasattr(video_result, 'url') and video_result.url:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"sync_video_{i+1}_{timestamp}.mp4"
                    save_video_from_url(video_result.url, filename)
        
    except Exception as e:
        print(f"❌ 同步生成失败（可能不支持同步模式）: {e}")


def interactive_video_generator(client):
    """交互式视频生成器"""
    print("\n🎮 交互式视频生成器 (输入 'quit' 退出):")
    print("="*60)
    
    while True:
        try:
            user_prompt = input("\n🎬 请输入视频描述: ").strip()
            
            if user_prompt.lower() in ['quit', 'exit', '退出']:
                print("👋 再见！")
                break
            
            if not user_prompt:
                continue
            
            print("🎯 提交视频生成任务...")
            
            response = client.videos.text_to_video(
                model="sora-2",
                prompt=user_prompt,
                sync_mode=SyncMode.ASYNC,
                width=1024,
                height=576,
                duration=4,
                fps=24
            )
            
            print(f"✅ 任务提交成功！")
            print(f"📋 任务ID: {response.data.job_id}")
            
            # 询问是否要等待完成
            choice = input("是否等待任务完成？(y/n): ").strip().lower()
            if choice in ['y', 'yes', '是']:
                job_info = [{
                    "job_id": response.data.job_id,
                    "prompt": user_prompt,
                    "type": "interactive"
                }]
                poll_video_jobs(client, job_info)
            
        except KeyboardInterrupt:
            print("\n\n👋 收到中断信号，退出生成器...")
            break
        except Exception as e:
            print(f"❌ 生成失败: {e}")


def main():
    """主函数"""
    print("🎬 OneThing AI SDK - Sora 2 视频生成示例集合")
    print("="*80)
    
    try:
        # 文生视频示例
        client, text_jobs = text_to_video_example()
        
        # 图生视频示例
        image_jobs = image_to_video_example(client)
        
        # 同步视频生成示例
        sync_video_example(client)
        
        # 合并所有任务
        all_jobs = text_jobs + image_jobs
        
        if all_jobs:
            # 询问是否要轮询任务状态
            choice = input("\n是否要轮询任务完成状态？(y/n): ").strip().lower()
            if choice in ['y', 'yes', '是']:
                poll_video_jobs(client, all_jobs)
        
        # 询问是否要进行交互式生成
        print("\n" + "="*80)
        choice = input("是否要进行交互式视频生成？(y/n): ").strip().lower()
        if choice in ['y', 'yes', '是']:
            interactive_video_generator(client)
        
        # 关闭客户端
        client.close()
        print("\n✅ 视频生成示例运行完成！")
        print("📁 生成的视频会保存在当前目录中")
        
    except Exception as e:
        print(f"❌ 程序错误: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")


if __name__ == "__main__":
    main()