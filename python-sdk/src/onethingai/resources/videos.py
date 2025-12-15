"""
OneThing AI SDK 视频生成资源模块。

提供同步和异步的视频生成功能，支持文生视频和图生视频。
"""

from typing import Any, Callable, Dict, List, Optional, Union

from onethingai.transport import Transport, AsyncTransport
from onethingai.types import (
    InputImage,
    InputVideo,
    Status,
    SyncMode,
    VideoDataResponse,
    VideoJobType,
    VideoOutputConfig,
    VideoParameters,
    VideoResponse,
    VideoResult,
    VideoResultContainer,
)
from onethingai.errors import ValidationError


class Videos:
    """
    同步视频生成资源类。
    
    提供文生视频、图生视频等功能的同步实现。
    """

    def __init__(self, transport: Transport) -> None:
        """
        初始化视频资源。
        
        参数:
            transport: HTTP传输层实例
        """
        self._transport = transport

    def generate(
        self,
        *,
        model: str,
        prompt: str,
        job_type: Union[VideoJobType, str] = VideoJobType.TEXT2VIDEO,
        sync_mode: Union[SyncMode, str] = SyncMode.ASYNC,
        n: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        duration: Optional[int] = None,
        fps: Optional[int] = None,
        input_images: Optional[List[Union[InputImage, Dict[str, Any]]]] = None,
        input_videos: Optional[List[Union[InputVideo, Dict[str, Any]]]] = None,
        seed: Optional[int] = None,
        audio_enabled: bool = False,
        negative_prompt: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> VideoResponse:
        """
        生成视频。

        参数:
            model: 模型标识符
            prompt: 生成提示词
            job_type: 任务类型（text2video/image2video）
            sync_mode: 同步模式（sync/async）
            n: 生成视频数量
            width: 视频宽度
            height: 视频高度
            duration: 视频时长（秒）
            fps: 帧率
            input_images: 图生视频用的输入图片
            input_videos: 输入视频
            seed: 随机种子
            audio_enabled: 是否启用音频生成
            negative_prompt: 负面提示词
            extra: 额外参数
        
        返回:
            VideoResponse: 包含生成结果的响应对象
        """
        request = self._build_request(
            model=model,
            prompt=prompt,
            job_type=job_type,
            sync_mode=sync_mode,
            n=n,
            width=width,
            height=height,
            duration=duration,
            fps=fps,
            input_images=input_images,
            input_videos=input_videos,
            seed=seed,
            audio_enabled=audio_enabled,
            negative_prompt=negative_prompt,
            extra=extra,
            **kwargs,
        )

        response = self._transport.request("POST", "/generation", request)
        return self._parse_response(response)

    def text_to_video(
        self,
        *,
        model: str,
        prompt: str,
        sync_mode: Union[SyncMode, str] = SyncMode.ASYNC,
        n: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        duration: Optional[int] = None,
        fps: Optional[int] = None,
        seed: Optional[int] = None,
        audio_enabled: bool = False,
        negative_prompt: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> VideoResponse:
        """从文本生成视频。"""
        return self.generate(
            model=model,
            prompt=prompt,
            job_type=VideoJobType.TEXT2VIDEO,
            sync_mode=sync_mode,
            n=n,
            width=width,
            height=height,
            duration=duration,
            fps=fps,
            seed=seed,
            audio_enabled=audio_enabled,
            negative_prompt=negative_prompt,
            extra=extra,
            **kwargs,
        )

    def image_to_video(
        self,
        *,
        model: str,
        prompt: str,
        input_images: List[Union[InputImage, Dict[str, Any]]],
        sync_mode: Union[SyncMode, str] = SyncMode.ASYNC,
        n: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        duration: Optional[int] = None,
        fps: Optional[int] = None,
        seed: Optional[int] = None,
        audio_enabled: bool = False,
        negative_prompt: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> VideoResponse:
        """从图片生成视频。"""
        return self.generate(
            model=model,
            prompt=prompt,
            job_type=VideoJobType.IMAGE2VIDEO,
            sync_mode=sync_mode,
            input_images=input_images,
            n=n,
            width=width,
            height=height,
            duration=duration,
            fps=fps,
            seed=seed,
            audio_enabled=audio_enabled,
            negative_prompt=negative_prompt,
            extra=extra,
            **kwargs,
        )

    def get_job_status(self, job_id: str) -> VideoResponse:
        """获取视频生成任务的状态。"""
        response = self._transport.request("GET", f"/generation/job/{job_id}", None)
        return self._parse_response(response)

    def wait(
        self,
        job_id: str,
        *,
        max_attempts: int = 0,
        interval: float = 5.0,
        timeout: float = 600.0,
        on_progress: Optional[Callable[[float, Status], None]] = None,
    ) -> VideoResponse:
        """
        等待视频任务完成。

        参数:
            job_id: 任务标识符
            max_attempts: 最大轮询次数（0表示无限制）
            interval: 轮询间隔（秒，视频默认5秒）
            timeout: 最大等待时间（秒，视频默认10分钟）
            on_progress: 进度回调函数
        
        返回:
            VideoResponse: 完成后的任务响应
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
        job_type: Union[VideoJobType, str],
        sync_mode: Union[SyncMode, str],
        n: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        duration: Optional[int] = None,
        fps: Optional[int] = None,
        input_images: Optional[List[Union[InputImage, Dict[str, Any]]]] = None,
        input_videos: Optional[List[Union[InputVideo, Dict[str, Any]]]] = None,
        seed: Optional[int] = None,
        audio_enabled: bool = False,
        negative_prompt: Optional[str] = None,
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
            job_type = VideoJobType(job_type)
        if isinstance(sync_mode, str):
            sync_mode = SyncMode(sync_mode)

        request: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "job_type": job_type.value,
            "sync_mode": sync_mode.value,
        }

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
        if duration is not None:
            output_config["duration"] = duration
        if fps is not None:
            output_config["fps"] = fps

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

        # 输入视频
        if input_videos:
            parsed_videos = []
            for vid in input_videos:
                if isinstance(vid, InputVideo):
                    parsed_videos.append(vid.model_dump(exclude_none=True))
                elif isinstance(vid, dict):
                    parsed_videos.append(vid)
            parameters["input_videos"] = parsed_videos

        if parameters:
            request["parameters"] = parameters

        # 构建额外参数
        extra_params: Dict[str, Any] = {}
        if seed is not None:
            extra_params["seed"] = seed
        extra_params["audio_enabled"] = audio_enabled
        if negative_prompt:
            extra_params["negative_prompt"] = negative_prompt
        if extra:
            extra_params.update(extra)

        if extra_params:
            request["extra"] = extra_params

        # 添加其他关键字参数
        request.update(kwargs)

        return request

    def _parse_response(self, response: Dict[str, Any]) -> VideoResponse:
        """解析API响应为VideoResponse对象。"""
        data = response.get("data", {})
        
        # 解析结果（如果存在）
        result = None
        if "result" in data and data["result"]:
            result_data = data["result"].get("data", [])
            parsed_results = [VideoResult(**r) for r in result_data]
            result = VideoResultContainer(data=parsed_results)

        video_data = VideoDataResponse(
            job_id=data.get("job_id", ""),
            status=Status(data.get("status", "processing")),
            progress=data.get("progress", 0.0),
            created=data.get("created", 0),
            result=result,
            error=data.get("error"),
        )

        return VideoResponse(
            code=response.get("code", 0),
            data=video_data,
            request_id=response.get("request_id", ""),
            message=response.get("message", ""),
        )


class AsyncVideos:
    """
    异步视频生成资源类。
    
    提供文生视频、图生视频等功能的异步实现。
    """

    def __init__(self, transport: AsyncTransport) -> None:
        """
        初始化异步视频资源。
        
        参数:
            transport: 异步HTTP传输层实例
        """
        self._transport = transport

    async def generate(
        self,
        *,
        model: str,
        prompt: str,
        job_type: Union[VideoJobType, str] = VideoJobType.TEXT2VIDEO,
        sync_mode: Union[SyncMode, str] = SyncMode.ASYNC,
        n: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        duration: Optional[int] = None,
        fps: Optional[int] = None,
        input_images: Optional[List[Union[InputImage, Dict[str, Any]]]] = None,
        input_videos: Optional[List[Union[InputVideo, Dict[str, Any]]]] = None,
        seed: Optional[int] = None,
        audio_enabled: bool = False,
        negative_prompt: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> VideoResponse:
        """异步生成视频。"""
        request = self._build_request(
            model=model,
            prompt=prompt,
            job_type=job_type,
            sync_mode=sync_mode,
            n=n,
            width=width,
            height=height,
            duration=duration,
            fps=fps,
            input_images=input_images,
            input_videos=input_videos,
            seed=seed,
            audio_enabled=audio_enabled,
            negative_prompt=negative_prompt,
            extra=extra,
            **kwargs,
        )

        response = await self._transport.request("POST", "/generation", request)
        return self._parse_response(response)

    async def text_to_video(
        self,
        *,
        model: str,
        prompt: str,
        sync_mode: Union[SyncMode, str] = SyncMode.ASYNC,
        n: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        duration: Optional[int] = None,
        fps: Optional[int] = None,
        seed: Optional[int] = None,
        audio_enabled: bool = False,
        negative_prompt: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> VideoResponse:
        """异步从文本生成视频。"""
        return await self.generate(
            model=model,
            prompt=prompt,
            job_type=VideoJobType.TEXT2VIDEO,
            sync_mode=sync_mode,
            n=n,
            width=width,
            height=height,
            duration=duration,
            fps=fps,
            seed=seed,
            audio_enabled=audio_enabled,
            negative_prompt=negative_prompt,
            extra=extra,
            **kwargs,
        )

    async def image_to_video(
        self,
        *,
        model: str,
        prompt: str,
        input_images: List[Union[InputImage, Dict[str, Any]]],
        sync_mode: Union[SyncMode, str] = SyncMode.ASYNC,
        n: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        duration: Optional[int] = None,
        fps: Optional[int] = None,
        seed: Optional[int] = None,
        audio_enabled: bool = False,
        negative_prompt: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> VideoResponse:
        """异步从图片生成视频。"""
        return await self.generate(
            model=model,
            prompt=prompt,
            job_type=VideoJobType.IMAGE2VIDEO,
            sync_mode=sync_mode,
            input_images=input_images,
            n=n,
            width=width,
            height=height,
            duration=duration,
            fps=fps,
            seed=seed,
            audio_enabled=audio_enabled,
            negative_prompt=negative_prompt,
            extra=extra,
            **kwargs,
        )

    async def get_job_status(self, job_id: str) -> VideoResponse:
        """获取视频生成任务的状态。"""
        response = await self._transport.request("GET", f"/generation/job/{job_id}", None)
        return self._parse_response(response)

    async def wait(
        self,
        job_id: str,
        *,
        max_attempts: int = 0,
        interval: float = 5.0,
        timeout: float = 600.0,
        on_progress: Optional[Callable[[float, Status], None]] = None,
    ) -> VideoResponse:
        """异步等待视频任务完成。"""
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
        job_type: Union[VideoJobType, str],
        sync_mode: Union[SyncMode, str],
        n: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        duration: Optional[int] = None,
        fps: Optional[int] = None,
        input_images: Optional[List[Union[InputImage, Dict[str, Any]]]] = None,
        input_videos: Optional[List[Union[InputVideo, Dict[str, Any]]]] = None,
        seed: Optional[int] = None,
        audio_enabled: bool = False,
        negative_prompt: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """构建请求字典。"""
        if not model:
            raise ValidationError("model", "model 是必需的")
        if not prompt:
            raise ValidationError("prompt", "prompt 是必需的")

        if isinstance(job_type, str):
            job_type = VideoJobType(job_type)
        if isinstance(sync_mode, str):
            sync_mode = SyncMode(sync_mode)

        request: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "job_type": job_type.value,
            "sync_mode": sync_mode.value,
        }

        if n is not None:
            request["n"] = n

        parameters: Dict[str, Any] = {}

        output_config: Dict[str, Any] = {}
        if width is not None:
            output_config["width"] = width
        if height is not None:
            output_config["height"] = height
        if duration is not None:
            output_config["duration"] = duration
        if fps is not None:
            output_config["fps"] = fps

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

        if input_videos:
            parsed_videos = []
            for vid in input_videos:
                if isinstance(vid, InputVideo):
                    parsed_videos.append(vid.model_dump(exclude_none=True))
                elif isinstance(vid, dict):
                    parsed_videos.append(vid)
            parameters["input_videos"] = parsed_videos

        if parameters:
            request["parameters"] = parameters

        extra_params: Dict[str, Any] = {}
        if seed is not None:
            extra_params["seed"] = seed
        extra_params["audio_enabled"] = audio_enabled
        if negative_prompt:
            extra_params["negative_prompt"] = negative_prompt
        if extra:
            extra_params.update(extra)

        if extra_params:
            request["extra"] = extra_params

        request.update(kwargs)

        return request

    def _parse_response(self, response: Dict[str, Any]) -> VideoResponse:
        """解析API响应为VideoResponse对象。"""
        data = response.get("data", {})
        
        result = None
        if "result" in data and data["result"]:
            result_data = data["result"].get("data", [])
            parsed_results = [VideoResult(**r) for r in result_data]
            result = VideoResultContainer(data=parsed_results)

        video_data = VideoDataResponse(
            job_id=data.get("job_id", ""),
            status=Status(data.get("status", "processing")),
            progress=data.get("progress", 0.0),
            created=data.get("created", 0),
            result=result,
            error=data.get("error"),
        )

        return VideoResponse(
            code=response.get("code", 0),
            data=video_data,
            request_id=response.get("request_id", ""),
            message=response.get("message", ""),
        )
