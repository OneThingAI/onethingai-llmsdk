# OneThing AI Python SDK

OneThing AI Python SDK 提供对 OneThing AI 平台的完整访问，支持文本、图片和视频生成。

## 安装

```bash
pip install git+https://github.com/onethingai/onethingai-llmsdk.git#subdirectory=python-sdk
```

## 快速开始

```python
from onethingai import OnethingAI

# 初始化客户端
client = OnethingAI(api_key="your-api-key")
```

## 文本生成

### 自定义文本接口

```python
# 聊天对话
response = client.text.chat(
    model="gpt-4o",
    messages=[{"role": "user", "content": "你好"}]
)

# 响应生成
response = client.text.responses(
    model="gpt-4o",
    prompt="解释机器学习"
)
```

### OpenAI 兼容接口

```python
# 聊天完成
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "你好"}]
)

# 响应接口（如果可用）
if client.responses:
    response = client.responses.create(
        model="gpt-4o",
        prompt="解释机器学习"
    )
```

## 图片生成

```python
# 生成图片
response = client.images.generate(
    model="doubao-seedream-4-0-250828",
    prompt="一只可爱的小猫"
)

# 获取图片URL
if response.data and response.data.result:
    image_url = response.data.result.data[0].url
    print(f"图片URL: {image_url}")
```

## 视频生成

```python
# 文本生成视频
response = client.videos.text_to_video(
    model="sora-2",
    prompt="一朵花在阳光下绽放"
)

# 获取任务ID并等待完成
if response.data:
    job_id = response.data.job_id
    result = client.videos.wait(job_id)
    
    if result.data and result.data.result:
        video_url = result.data.result.data[0].url
        print(f"视频URL: {video_url}")
```

## 配置

```python
client = OnethingAI(
    api_key="your-api-key",
    base_url="https://api-model.onethingai.com/v2",  # 默认值
    timeout=60.0,
    max_retries=3
)
```

## 环境变量

```bash
export ONETHINGAI_API_KEY="your-api-key"
export ONETHINGAI_BASE_URL="https://api-model.onethingai.com/v2"
```

## 异步支持

```python
import asyncio
from onethingai import AsyncOnethingAI

async def main():
    async with AsyncOnethingAI(api_key="your-api-key") as client:
        # 只有图片和视频支持异步
        response = await client.images.generate(
            model="doubao-seedream-4-0-250828",
            prompt="美丽的风景"
        )

asyncio.run(main())
```

## 示例

查看 [examples](./examples/) 目录获取更多使用示例。

## 许可证

MIT License
