"""
OneThing AI SDK 客户端模块

提供与 OneThing AI API 交互的主要客户端类。
所有请求统一使用 v2 API 接口，确保一致性和最佳性能。
同时提供自定义文本功能和 OpenAI 兼容性。
"""

import os
from typing import Any, Dict, Optional

import openai
from openai import OpenAI, AsyncOpenAI

from onething_llm.transport import Transport, AsyncTransport
from onething_llm.resources.text import Text
from onething_llm.resources.images import Images, AsyncImages
from onething_llm.resources.videos import Videos, AsyncVideos
from onething_llm.errors import OnethingLLMError


# 默认配置
DEFAULT_BASE_URL = "https://api-model.onethingai.com/v2"
DEFAULT_TIMEOUT = 60.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_POLLING_INTERVAL = 2.0


class OnethingLLM:
    """
    OneThing AI LLM SDK 客户端

    该客户端提供以下功能:
    - 自定义文本生成: client.text.chat(), client.text.completions(), client.text.responses()
    - OpenAI 兼容接口: client.chat.completions.create(), client.completions.create(), client.responses.create()
    - 图片生成: client.images.generate()
    - 视频生成: client.videos.generate()

    使用示例:
        ```python
        from onething_llm import OnethingLLM

        client = OnethingLLM(api_key="your-api-key")

        # 自定义文本生成 (使用 /generation 接口，通过 job_type 区分)
        response = client.text.chat(
            model="gpt-4o",
            messages=[{"role": "user", "content": "你好!"}]
        )
        
        response = client.text.completions(
            model="gpt-4o",
            prompt="你好"
        )
        
        response = client.text.responses(
            model="gpt-4o",
            prompt="你好"
        )

        # OpenAI 兼容接口 (使用标准 OpenAI API)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "你好!"}]
        )
        
        response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt="你好"
        )
        
        response = client.responses.create(
            model="gpt-4o",
            prompt="你好"
        )

        # 图片生成
        response = client.images.generate(
            model="doubao-seedream-4-0-250828",
            prompt="美丽的日落"
        )

        # 视频生成
        response = client.videos.generate(
            model="sora-2",
            prompt="一只猫在玩耍"
        )
        ```
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        polling_interval: float = DEFAULT_POLLING_INTERVAL,
        headers: Optional[Dict[str, str]] = None,
        openai_client: Optional[OpenAI] = None,
    ) -> None:
        """
        初始化 OneThing AI 客户端

        Args:
            api_key: 用于认证的 API 密钥。如果未提供，将从 ONETHING_LLM_API_KEY 环境变量获取。
            base_url: API 基础地址。默认为 https://api-model.onethingai.com/v2
            timeout: 请求超时时间（秒）
            max_retries: 请求失败时的最大重试次数
            polling_interval: 轮询异步任务的间隔时间（秒）
            headers: 请求中包含的自定义头部
            openai_client: 可选的预配置 OpenAI 客户端，用于 OpenAI 兼容功能
        """
        # 如果未提供，从环境变量获取 API 密钥
        self._api_key = api_key or os.environ.get("ONETHING_LLM_API_KEY", "")
        if not self._api_key:
            raise OnethingLLMError("API 密钥是必需的。请设置 ONETHING_LLM_API_KEY 环境变量或传入 api_key 参数。")

        # 如果未提供，从环境变量获取基础地址
        self._base_url = base_url or os.environ.get("ONETHING_LLM_BASE_URL", DEFAULT_BASE_URL)
        self._timeout = timeout
        self._max_retries = max_retries
        self._polling_interval = polling_interval
        self._headers = headers or {}

        # 初始化统一的传输层，所有自定义请求都使用 v2 API
        self._transport = Transport(
            base_url=self._base_url,
            api_key=self._api_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )

        # 初始化 OpenAI 兼容客户端
        if openai_client:
            self._openai_client = openai_client
        else:
            self._openai_client = OpenAI(
                api_key=self._api_key,
                base_url=self._base_url+"/openai",
                timeout=timeout,
                max_retries=max_retries,
                default_headers=headers,
            )

        # 初始化所有资源
        self._text = Text(self._transport)  # 自定义文本功能
        self._images = Images(self._transport)
        self._videos = Videos(self._transport)

    @property
    def text(self) -> Text:
        """访问自定义文本生成资源 (包含 chat、completions、responses 三个函数)"""
        return self._text

    @property
    def chat(self) -> openai.resources.Chat:
        """访问 OpenAI 兼容聊天补全资源"""
        return self._openai_client.chat

    @property
    def completions(self) -> openai.resources.Completions:
        """访问 OpenAI 兼容文本补全资源"""
        return self._openai_client.completions

    @property
    def responses(self):
        """访问 OpenAI 兼容响应资源"""
        return getattr(self._openai_client, 'responses', None)

    @property
    def images(self) -> Images:
        """访问图片生成资源"""
        return self._images

    @property
    def videos(self) -> Videos:
        """访问视频生成资源"""
        return self._videos

    @property
    def models(self) -> openai.resources.Models:
        """访问 OpenAI 兼容模型资源"""
        return self._openai_client.models

    def close(self) -> None:
        """关闭客户端并释放资源"""
        self._transport.close()
        self._openai_client.close()

    def __enter__(self) -> "OnethingLLM":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncOnethingLLM:
    """
    异步 OneThing AI LLM SDK 客户端

    该客户端提供对 OneThing AI 服务的异步访问。

    使用示例:
        ```python
        import asyncio
        from onething_llm import AsyncOnethingLLM

        async def main():
            client = AsyncOnethingLLM(api_key="your-api-key")

            # 异步图片生成
            response = await client.images.generate(
                model="doubao-seedream-4-0-250828",
                prompt="美丽的日落"
            )

            # 异步视频生成
            response = await client.videos.generate(
                model="sora-2",
                prompt="一只猫在玩耍"
            )

            await client.close()

        asyncio.run(main())
        ```
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        polling_interval: float = DEFAULT_POLLING_INTERVAL,
        headers: Optional[Dict[str, str]] = None,
        openai_client: Optional[AsyncOpenAI] = None,
    ) -> None:
        """
        初始化异步 OneThing AI 客户端

        Args:
            api_key: 用于认证的 API 密钥
            base_url: API 基础地址
            timeout: 请求超时时间（秒）
            max_retries: 请求失败时的最大重试次数
            polling_interval: 轮询异步任务的间隔时间（秒）
            headers: 请求中包含的自定义头部
            openai_client: 可选的预配置 AsyncOpenAI 客户端
        """
        self._api_key = api_key or os.environ.get("ONETHING_LLM_API_KEY", "")
        if not self._api_key:
            raise OnethingLLMError("API 密钥是必需的。请设置 ONETHING_LLM_API_KEY 环境变量或传入 api_key 参数。")

        self._base_url = base_url or os.environ.get("ONETHING_LLM_BASE_URL", DEFAULT_BASE_URL)
        self._timeout = timeout
        self._max_retries = max_retries
        self._polling_interval = polling_interval
        self._headers = headers or {}

        # 为图片/视频初始化异步传输层
        self._transport = AsyncTransport(
            base_url=self._base_url,
            api_key=self._api_key,
            timeout=timeout,
            max_retries=max_retries,
            headers=headers,
        )

        # 初始化 AsyncOpenAI 客户端 (用于 OpenAI 兼容功能)
        if openai_client:
            self._openai_client = openai_client
        else:
            self._openai_client = AsyncOpenAI(
                api_key=self._api_key,
                base_url=self._base_url+"/openai",
                timeout=timeout,
                max_retries=max_retries,
                default_headers=headers,
            )

        # 初始化资源 (只有图片和视频有异步版本)
        self._images = AsyncImages(self._transport)
        self._videos = AsyncVideos(self._transport)

    @property
    def images(self) -> AsyncImages:
        """访问异步图片生成资源"""
        return self._images

    @property
    def videos(self) -> AsyncVideos:
        """访问异步视频生成资源"""
        return self._videos

    @property
    def models(self) -> openai.resources.AsyncModels:
        """访问 OpenAI 兼容异步模型资源"""
        return self._openai_client.models

    async def close(self) -> None:
        """关闭客户端并释放资源"""
        await self._transport.close()
        await self._openai_client.close()

    async def __aenter__(self) -> "AsyncOnethingLLM":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

