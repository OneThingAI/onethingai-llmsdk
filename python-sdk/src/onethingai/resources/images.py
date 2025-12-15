"""
OneThing AI SDK 图片生成资源模块。

提供同步和异步的图片生成、编辑等功能。
"""

from typing import Any, Callable, Dict, Iterator, List, Optional, Union

from onethingai.transport import Transport, AsyncTransport
from onethingai.types import (
    ImageDataResponse,
    ImageExtra,
    ImageJobType,
    ImageOutputConfig,
    ImageParameters,
    ImageRequest,
    ImageResponse,
    ImageResult,
    ImageResultContainer,
    InputImage,
    PollingOptions,
    ResponseFormat,
    Status,
    SyncMode,
)
from onethingai.stream import StreamReader, AsyncStreamReader
from onethingai.errors import ValidationError


class Images:
    """
    同步图片生成资源类。
    
    提供图片生成、编辑、变体等功能的同步实现。
    """

    def __init__(self, transport: Transport) -> None:
        """
        初始化图片资源。
        
        参数:
            transport: HTTP传输层实例
        """
        self._transport = transport

    def generate(
        self,
        *,
        model: str,
        prompt: str,
        job_type: Union[ImageJobType, str] = ImageJobType.GENERATION,
        n: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        response_format: Optional[Union[ResponseFormat, str]] = None,
        input_images: Optional[List[Union[InputImage, Dict[str, Any]]]] = None,
        seed: Optional[int] = None,
        style: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> ImageResponse:
        """
        生成图片。

        参数:
            model: 模型标识符
            prompt: 生成提示词
            job_type: 任务类型（generation/edit/variation）
            n: 生成图片数量
            width: 图片宽度
            height: 图片高度
            response_format: 响应格式（url或b64_json）
            input_images: 编辑用的输入图片
            seed: 随机种子
            style: 图片风格（vivid或natural）
            extra: 额外参数
        
        返回:
            ImageResponse: 包含生成结果的响应对象
        """
        request = self._build_request(
            model=model,
            prompt=prompt,
            job_type=job_type,
            sync_mode=SyncMode.SYNC,
            stream=False,
            n=n,
            width=width,
            height=height,
            response_format=response_format,
            input_images=input_images,
            seed=seed,
            style=style,
            extra=extra,
            **kwargs,
        )

        response = self._transport.request("POST", "/generation", request)
        return self._parse_response(response)

    def generate_stream(
        self,
        *,
        model: str,
        prompt: str,
        job_type: Union[ImageJobType, str] = ImageJobType.GENERATION,
        n: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        response_format: Optional[Union[ResponseFormat, str]] = None,
        input_images: Optional[List[Union[InputImage, Dict[str, Any]]]] = None,
        seed: Optional[int] = None,
        style: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> StreamReader[ImageResult]:
        """
        流式生成图片。

        返回流事件的迭代器，可实时获取生成进度。
        """
        request = self._build_request(
            model=model,
            prompt=prompt,
            job_type=job_type,
            sync_mode=SyncMode.SYNC,
            stream=True,
            n=n,
            width=width,
            height=height,
            response_format=response_format,
            input_images=input_images,
            seed=seed,
            style=style,
            extra=extra,
            **kwargs,
        )

        lines = self._transport.stream_request("POST", "/generation", request)
        return StreamReader(lines, ImageResult)

    def edit(
        self,
        *,
        model: str,
        prompt: str,
        input_images: List[Union[InputImage, Dict[str, Any]]],
        n: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        response_format: Optional[Union[ResponseFormat, str]] = None,
        seed: Optional[int] = None,
        style: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> ImageResponse:
        """
        编辑图片。

        参数:
            model: 模型标识符
            prompt: 编辑指令
            input_images: 要编辑的源图片
            其他参数与generate相同
        
        返回:
            ImageResponse: 包含编辑后图片的响应对象
        """
        return self.generate(
            model=model,
            prompt=prompt,
            job_type=ImageJobType.EDIT,
            input_images=input_images,
            n=n,
            width=width,
            height=height,
            response_format=response_format,
            seed=seed,
            style=style,
            extra=extra,
            **kwargs,
        )

    def edit_stream(
        self,
        *,
        model: str,
        prompt: str,
        input_images: List[Union[InputImage, Dict[str, Any]]],
        n: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        response_format: Optional[Union[ResponseFormat, str]] = None,
        seed: Optional[int] = None,
        style: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> StreamReader[ImageResult]:
        """流式编辑图片。"""
        return self.generate_stream(
            model=model,
            prompt=prompt,
            job_type=ImageJobType.EDIT,
            input_images=input_images,
            n=n,
            width=width,
            height=height,
            response_format=response_format,
            seed=seed,
            style=style,
            extra=extra,
            **kwargs,
        )

    def get_job_status(self, job_id: str) -> ImageResponse:
        """获取图片生成任务的状态。"""
        response = self._transport.request("GET", f"/generation/job/{job_id}", None)
        return self._parse_response(response)

    def wait(
        self,
        job_id: str,
        *,
        max_attempts: int = 0,
        interval: float = 2.0,
        timeout: float = 300.0,
        on_progress: Optional[Callable[[float, Status], None]] = None,
    ) -> ImageResponse:
        """
        等待图片任务完成。

        参数:
            job_id: 任务标识符
            max_attempts: 最大轮询次数（0表示无限制）
            interval: 轮询间隔（秒）
            timeout: 最大等待时间（秒，0表示无超时）
            on_progress: 进度回调函数
        
        返回:
            ImageResponse: 完成后的任务响应
        """
        import time
        
        start_time = time.time()
        attempts = 0

        while True:
            if max_attempts > 0 and attempts >= max_attempts:
                from onethingai.errors import TimeoutError
                raise TimeoutError(f"超过最大轮询次数 ({max_attempts})")

            if timeout > 0 and (time.time() - start_time) > timeout:
                from onethingai.errors import TimeoutError
                raise TimeoutError(f"轮询超时 ({timeout}秒)")

            response = self.get_job_status(job_id)
            
            if on_progress:
                on_progress(response.data.progress, response.data.status)

            if response.data.is_completed():
                return response

            if response.data.is_failed():
                from onethingai.errors import JobError
                raise JobError(
                    f"任务失败: {response.data.error}",
                    job_id=job_id,
                    error_details=response.data.error,
                )

            time.sleep(interval)
            attempts += 1

    def _build_request(
        self,
        *,
        model: str,
        prompt: str,
        job_type: Union[ImageJobType, str],
        sync_mode: SyncMode,
        stream: bool,
        n: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        response_format: Optional[Union[ResponseFormat, str]] = None,
        input_images: Optional[List[Union[InputImage, Dict[str, Any]]]] = None,
        seed: Optional[int] = None,
        style: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """构建请求字典。"""
        if not model:
            raise ValidationError("model", "model 是必需的")
        if not prompt:
            raise ValidationError("prompt", "prompt 是必需的")

        # 如果是字符串则转换为枚举
        if isinstance(job_type, str):
            job_type = ImageJobType(job_type)

        # 如果是字符串则转换为枚举
        if isinstance(response_format, str):
            response_format = ResponseFormat(response_format)

        request: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "job_type": job_type.value,
            "sync_mode": sync_mode.value,
        }

        if stream:
            request["stream"] = True

        if n is not None:
            request["n"] = n

        # 构建参数
        parameters: Dict[str, Any] = {}

        # 输出配置
        output_config: Dict[str, Any] = {}
        if width is not None:
            output_config["width"] = width
        if height is not None:
            output_config["height"] = height
        if response_format is not None:
            output_config["response_format"] = response_format.value

        if output_config:
            parameters["output_config"] = output_config

        # 输入图片
        if input_images:
            parsed_images = []
            for img in input_images:
                if isinstance(img, InputImage):
                    parsed_images.append(img.model_dump(exclude_none=True))
                elif isinstance(img, dict):
                    parsed_images.append(img)
            parameters["input_images"] = parsed_images

        if parameters:
            request["parameters"] = parameters

        # 构建额外参数
        extra_params: Dict[str, Any] = {}
        if seed is not None:
            extra_params["seed"] = seed
        if style is not None:
            extra_params["style"] = style
        if extra:
            extra_params.update(extra)

        if extra_params:
            request["extra"] = extra_params

        # 添加其他关键字参数
        request.update(kwargs)

        return request

    def _parse_response(self, response: Dict[str, Any]) -> ImageResponse:
        """解析API响应为ImageResponse对象"""
        # 直接使用新的ImageResponse类型解析
        return ImageResponse(**response)


class AsyncImages:
    """
    异步图片生成资源类。
    
    提供图片生成、编辑、变体等功能的异步实现。
    """

    def __init__(self, transport: AsyncTransport) -> None:
        """
        初始化异步图片资源。
        
        参数:
            transport: 异步HTTP传输层实例
        """
        self._transport = transport

    async def generate(
        self,
        *,
        model: str,
        prompt: str,
        job_type: Union[ImageJobType, str] = ImageJobType.GENERATION,
        n: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        response_format: Optional[Union[ResponseFormat, str]] = None,
        input_images: Optional[List[Union[InputImage, Dict[str, Any]]]] = None,
        seed: Optional[int] = None,
        style: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> ImageResponse:
        """异步生成图片。"""
        request = self._build_request(
            model=model,
            prompt=prompt,
            job_type=job_type,
            sync_mode=SyncMode.SYNC,
            stream=False,
            n=n,
            width=width,
            height=height,
            response_format=response_format,
            input_images=input_images,
            seed=seed,
            style=style,
            extra=extra,
            **kwargs,
        )

        response = await self._transport.request("POST", "/generation", request)
        return self._parse_response(response)

    async def generate_stream(
        self,
        *,
        model: str,
        prompt: str,
        job_type: Union[ImageJobType, str] = ImageJobType.GENERATION,
        n: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        response_format: Optional[Union[ResponseFormat, str]] = None,
        input_images: Optional[List[Union[InputImage, Dict[str, Any]]]] = None,
        seed: Optional[int] = None,
        style: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> AsyncStreamReader[ImageResult]:
        """异步流式生成图片。"""
        request = self._build_request(
            model=model,
            prompt=prompt,
            job_type=job_type,
            sync_mode=SyncMode.SYNC,
            stream=True,
            n=n,
            width=width,
            height=height,
            response_format=response_format,
            input_images=input_images,
            seed=seed,
            style=style,
            extra=extra,
            **kwargs,
        )

        lines = self._transport.stream_request("POST", "/generation", request)
        return AsyncStreamReader(lines, ImageResult)

    async def edit(
        self,
        *,
        model: str,
        prompt: str,
        input_images: List[Union[InputImage, Dict[str, Any]]],
        n: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        response_format: Optional[Union[ResponseFormat, str]] = None,
        seed: Optional[int] = None,
        style: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> ImageResponse:
        """异步编辑图片。"""
        return await self.generate(
            model=model,
            prompt=prompt,
            job_type=ImageJobType.EDIT,
            input_images=input_images,
            n=n,
            width=width,
            height=height,
            response_format=response_format,
            seed=seed,
            style=style,
            extra=extra,
            **kwargs,
        )

    async def edit_stream(
        self,
        *,
        model: str,
        prompt: str,
        input_images: List[Union[InputImage, Dict[str, Any]]],
        n: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        response_format: Optional[Union[ResponseFormat, str]] = None,
        seed: Optional[int] = None,
        style: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> AsyncStreamReader[ImageResult]:
        """异步流式编辑图片。"""
        return await self.generate_stream(
            model=model,
            prompt=prompt,
            job_type=ImageJobType.EDIT,
            input_images=input_images,
            n=n,
            width=width,
            height=height,
            response_format=response_format,
            seed=seed,
            style=style,
            extra=extra,
            **kwargs,
        )

    async def get_job_status(self, job_id: str) -> ImageResponse:
        """获取图片生成任务的状态。"""
        response = await self._transport.request("GET", f"/generation/job/{job_id}", None)
        return self._parse_response(response)

    async def wait(
        self,
        job_id: str,
        *,
        max_attempts: int = 0,
        interval: float = 2.0,
        timeout: float = 300.0,
        on_progress: Optional[Callable[[float, Status], None]] = None,
    ) -> ImageResponse:
        """异步等待图片任务完成。"""
        import asyncio
        import time
        
        start_time = time.time()
        attempts = 0

        while True:
            if max_attempts > 0 and attempts >= max_attempts:
                from onethingai.errors import TimeoutError
                raise TimeoutError(f"超过最大轮询次数 ({max_attempts})")

            if timeout > 0 and (time.time() - start_time) > timeout:
                from onethingai.errors import TimeoutError
                raise TimeoutError(f"轮询超时 ({timeout}秒)")

            response = await self.get_job_status(job_id)
            
            if on_progress:
                on_progress(response.data.progress, response.data.status)

            if response.data.is_completed():
                return response

            if response.data.is_failed():
                from onethingai.errors import JobError
                raise JobError(
                    f"任务失败: {response.data.error}",
                    job_id=job_id,
                    error_details=response.data.error,
                )

            await asyncio.sleep(interval)
            attempts += 1

    def _build_request(
        self,
        *,
        model: str,
        prompt: str,
        job_type: Union[ImageJobType, str],
        sync_mode: SyncMode,
        stream: bool,
        n: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        response_format: Optional[Union[ResponseFormat, str]] = None,
        input_images: Optional[List[Union[InputImage, Dict[str, Any]]]] = None,
        seed: Optional[int] = None,
        style: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """构建请求字典。"""
        if not model:
            raise ValidationError("model", "model 是必需的")
        if not prompt:
            raise ValidationError("prompt", "prompt 是必需的")

        if isinstance(job_type, str):
            job_type = ImageJobType(job_type)

        if isinstance(response_format, str):
            response_format = ResponseFormat(response_format)

        request: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "job_type": job_type.value,
            "sync_mode": sync_mode.value,
        }

        if stream:
            request["stream"] = True

        if n is not None:
            request["n"] = n

        parameters: Dict[str, Any] = {}

        output_config: Dict[str, Any] = {}
        if width is not None:
            output_config["width"] = width
        if height is not None:
            output_config["height"] = height
        if response_format is not None:
            output_config["response_format"] = response_format.value

        if output_config:
            parameters["output_config"] = output_config

        if input_images:
            parsed_images = []
            for img in input_images:
                if isinstance(img, InputImage):
                    parsed_images.append(img.model_dump(exclude_none=True))
                elif isinstance(img, dict):
                    parsed_images.append(img)
            parameters["input_images"] = parsed_images

        if parameters:
            request["parameters"] = parameters

        extra_params: Dict[str, Any] = {}
        if seed is not None:
            extra_params["seed"] = seed
        if style is not None:
            extra_params["style"] = style
        if extra:
            extra_params.update(extra)

        if extra_params:
            request["extra"] = extra_params

        request.update(kwargs)

        return request

    def _parse_response(self, response: Dict[str, Any]) -> ImageResponse:
        """解析API响应为ImageResponse对象"""
        # 直接使用新的ImageResponse类型解析
        return ImageResponse(**response)
