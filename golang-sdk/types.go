package onethingai

import (
	"encoding/json"
	"fmt"
)

// ==================== Request Types ====================

// SyncMode 同步模式枚举
type SyncMode string

const (
	SyncModeSync  SyncMode = "sync"  // 同步
	SyncModeAsync SyncMode = "async" // 异步
)

// InputImage 输入图片结构
type InputImage struct {
	URL     *string `json:"url,omitempty"`
	B64JSON *string `json:"b64_json,omitempty"`
}

// InputVideo 输入视频结构
type InputVideo struct {
	URL *string `json:"url,omitempty"`
}

// ResponseFormat 响应格式枚举
type ResponseFormat string

const (
	ResponseFormatURL     ResponseFormat = "url"
	ResponseFormatB64JSON ResponseFormat = "b64_json"
)

// ==================== Job Types ====================

// ImageJobType 图片任务类型枚举
type ImageJobType string

const (
	ImageJobTypeGeneration ImageJobType = "generation"
	ImageJobTypeEdit       ImageJobType = "edit"
	ImageJobTypeVariation  ImageJobType = "variation"
)

// VideoJobType 视频任务类型枚举
type VideoJobType string

const (
	VideoJobTypeText2Video  VideoJobType = "text2video"  // 文本到视频
	VideoJobTypeImage2Video VideoJobType = "image2video" // 图片到视频
)

// TextJobType 文本任务类型枚举
type TextJobType string

const (
	TextJobTypeChatCompletions TextJobType = "chat/completions"
	TextJobTypeCompletions     TextJobType = "completions"
	TextJobTypeResponses       TextJobType = "responses"
)

// ==================== Output Config ====================

// ImageOutputConfig 图片输出配置
type ImageOutputConfig struct {
	Height         *int            `json:"height,omitempty"`
	Width          *int            `json:"width,omitempty"`
	ResponseFormat *ResponseFormat `json:"response_format,omitempty"`
}

// VideoOutputConfig 视频输出配置
type VideoOutputConfig struct {
	Height   *int `json:"height,omitempty"`
	Width    *int `json:"width,omitempty"`
	Duration *int `json:"duration,omitempty"` // 视频时长（秒）
	Fps      *int `json:"fps,omitempty"`      // 视频帧率
}

// ==================== Extra Params ====================

// ImageExtra 图片额外参数
type ImageExtra struct {
	Seed  *int        `json:"seed,omitempty"`
	Style *ImageStyle `json:"style,omitempty"`
}

// ImageStyle 图片风格枚举
type ImageStyle string

const (
	ImageStyleVivid   ImageStyle = "vivid"   // 生动风格
	ImageStyleNatural ImageStyle = "natural" // 自然风格
)

// MarshalJSON for ImageStyle
func (s ImageStyle) MarshalJSON() ([]byte, error) {
	return json.Marshal(string(s))
}

// UnmarshalJSON for ImageStyle
func (s *ImageStyle) UnmarshalJSON(data []byte) error {
	var str string
	if err := json.Unmarshal(data, &str); err != nil {
		return err
	}
	*s = ImageStyle(str)
	return nil
}

// VideoExtra 视频额外参数
type VideoExtra struct {
	Seed           *int   `json:"seed,omitempty"`
	AudioEnable    bool   `json:"audio_enabled"`
	NegativePrompt string `json:"negative_prompt,omitempty"` // 反向提示词
}

// ==================== Parameters ====================

// Parameters 通用参数配置
type Parameters[T any] struct {
	InputImages  []InputImage `json:"input_images,omitempty"`
	InputVideos  []InputVideo `json:"input_videos,omitempty"`
	OutputConfig *T           `json:"output_config,omitempty"`
}

// ==================== Unified Request ====================

// UnifiedRequest 统一请求结构
type UnifiedRequest[T any, F any, S any] struct {
	Model      string         `json:"model"`                // 使用的模型或引擎的唯一标识符
	JobType    F              `json:"job_type"`             // 任务类型
	SyncMode   SyncMode       `json:"sync_mode"`            // 响应模式
	Stream     *bool          `json:"stream,omitempty"`     // 是否启用流式响应
	Prompt     string         `json:"prompt"`               // 核心文本描述或编辑指令
	N          *int           `json:"n,omitempty"`          // 期望生成的图片/视频数量
	Parameters *Parameters[T] `json:"parameters,omitempty"` // 结构化通用配置
	Extra      *S             `json:"extra,omitempty"`      // 额外参数
}

// ImageRequest 图片请求类型
type ImageRequest = UnifiedRequest[ImageOutputConfig, ImageJobType, ImageExtra]

// VideoRequest 视频请求类型
type VideoRequest = UnifiedRequest[VideoOutputConfig, VideoJobType, VideoExtra]

// ==================== Response Types ====================

// Status 任务状态枚举
type Status string

const (
	StatusProcessing Status = "processing" // 处理中
	StatusSuccess    Status = "success"    // 已完成
	StatusFailed     Status = "failed"     // 失败
)

// MarshalJSON for Status
func (s Status) MarshalJSON() ([]byte, error) {
	return json.Marshal(string(s))
}

// UnmarshalJSON for Status
func (s *Status) UnmarshalJSON(data []byte) error {
	var str string
	if err := json.Unmarshal(data, &str); err != nil {
		return err
	}
	*s = Status(str)
	return nil
}

// Result 任务结果
type Result[T any] struct {
	Data []T `json:"data"` // 生成或编辑结果的列表
}

// ImageAndVideoDataResponse 统一响应结构
type ImageAndVideoDataResponse[T any] struct {
	JobID    string     `json:"job_id"`           // 任务ID
	Status   Status     `json:"status"`           // 任务状态
	Progress float64    `json:"progress"`         // 任务完成百分比 (0.0 到 1.0)
	Created  int64      `json:"created"`          // Unix 时间戳，表示结果创建时间
	Result   *Result[T] `json:"result,omitempty"` // 任务成功完成时的结果
	Error    any        `json:"error,omitempty"`  // 任务失败时的错误信息
}

// GetProgress returns the task progress
func (r *ImageAndVideoDataResponse[T]) GetProgress() float64 {
	return r.Progress
}

// GetStatus returns the task status
func (r *ImageAndVideoDataResponse[T]) GetStatus() Status {
	return r.Status
}

// GetError returns the task error
func (r *ImageAndVideoDataResponse[T]) GetError() any {
	return r.Error
}

// IsCompleted 判断任务是否完成
func (r *ImageAndVideoDataResponse[T]) IsCompleted() bool {
	return r.Status == StatusSuccess
}

// IsFailed 判断任务是否失败
func (r *ImageAndVideoDataResponse[T]) IsFailed() bool {
	return r.Status == StatusFailed
}

// IsProcessing 判断任务是否处理中
func (r *ImageAndVideoDataResponse[T]) IsProcessing() bool {
	return r.Status == StatusProcessing
}

// ImageDataResponse 图片响应类型
type ImageDataResponse = ImageAndVideoDataResponse[ImageResult]

// VideoDataResponse 视频响应类型
type VideoDataResponse = ImageAndVideoDataResponse[VideoResult]

// ==================== Result Types ====================

// ImageResult 图片结果
type ImageResult struct {
	Index    int                    `json:"index"`              // 结果索引
	URL      *string                `json:"url,omitempty"`      // 生成图片的URL
	B64JSON  *string                `json:"b64_json,omitempty"` // 生成图片的Base64编码,含dataurl前缀
	Metadata map[string]interface{} `json:"metadata,omitempty"` // 结果相关的元数据
}

// GetURL returns the image URL or empty string
func (r *ImageResult) GetURL() string {
	if r.URL != nil {
		return *r.URL
	}
	return ""
}

// GetB64JSON returns the base64 image or empty string
func (r *ImageResult) GetB64JSON() string {
	if r.B64JSON != nil {
		return *r.B64JSON
	}
	return ""
}

// VideoResult 视频结果
type VideoResult struct {
	Index    int                    `json:"index"`              // 结果索引
	URL      *string                `json:"url,omitempty"`      // 生成视频的URL
	Duration *int                   `json:"duration,omitempty"` // 视频时长（秒）
	Fps      *int                   `json:"fps,omitempty"`      // 视频帧率
	Metadata map[string]interface{} `json:"metadata,omitempty"` // 结果相关的元数据
}

// GetURL returns the video URL or empty string
func (r *VideoResult) GetURL() string {
	if r.URL != nil {
		return *r.URL
	}
	return ""
}

// GetDuration returns the video duration or 0
func (r *VideoResult) GetDuration() int {
	if r.Duration != nil {
		return *r.Duration
	}
	return 0
}

// GetFps returns the video FPS or 0
func (r *VideoResult) GetFps() int {
	if r.Fps != nil {
		return *r.Fps
	}
	return 0
}

// ==================== Stream Types ====================

// StreamEventType 流式事件类型枚举
type StreamEventType string

const (
	EventTypeProgress      StreamEventType = "progress"       // 进度更新
	EventTypePartialResult StreamEventType = "partial_result" // 部分结果
	EventTypeError         StreamEventType = "error"          // 错误
	EventTypeDone          StreamEventType = "done"           // 完成
)

// MarshalJSON for StreamEventType
func (e StreamEventType) MarshalJSON() ([]byte, error) {
	return json.Marshal(string(e))
}

// UnmarshalJSON for StreamEventType
func (e *StreamEventType) UnmarshalJSON(data []byte) error {
	var str string
	if err := json.Unmarshal(data, &str); err != nil {
		return err
	}
	*e = StreamEventType(str)
	return nil
}

// StreamDataResponse 流式响应结构
type StreamDataResponse[T any] struct {
	Type  StreamEventType `json:"type"`            // 流式消息的类型
	Data  T               `json:"data,omitempty"`  // 事件负载数据
	Error any             `json:"error,omitempty"` // 错误信息
}

// IsProgress 判断是否为进度事件
func (s *StreamDataResponse[T]) IsProgress() bool {
	return s.Type == EventTypeProgress
}

// IsPartialResult 判断是否为部分结果事件
func (s *StreamDataResponse[T]) IsPartialResult() bool {
	return s.Type == EventTypePartialResult
}

// IsError 判断是否为错误事件
func (s *StreamDataResponse[T]) IsError() bool {
	return s.Type == EventTypeError
}

// IsDone 判断是否为完成事件
func (s *StreamDataResponse[T]) IsDone() bool {
	return s.Type == EventTypeDone
}

// ImageStreamDataResponse 图片流式响应类型
type ImageStreamDataResponse = StreamDataResponse[ImageResult]

// VideoStreamDataResponse 视频流式响应类型
type VideoStreamDataResponse = StreamDataResponse[VideoResult]

// TextDataResponse 文本数据结果
type TextDataResponse = map[string]interface{}

type Response[T any] struct {
	Code      int    `json:"code"`
	Data      T      `json:"data"`
	RequestID string `json:"request_id"`
	Message   string `json:"message"`
}

type TextResponse = Response[TextDataResponse]
type ImageResponse = Response[ImageDataResponse]
type VideoResponse = Response[VideoDataResponse]

func NewTextResponse(val interface{}) (*TextResponse, error) {
	return NewResponse[TextDataResponse](val)
}

func NewImageResponse(val interface{}) (*ImageResponse, error) {
	return NewResponse[ImageDataResponse](val)
}

func NewVideoResponse(val interface{}) (*VideoResponse, error) {
	return NewResponse[VideoDataResponse](val)
}

func NewResponse[T any](val interface{}) (*Response[T], error) {
	switch v := val.(type) {
	case map[string]interface{}:
		rbytes, err := json.Marshal(v)
		if err != nil {
			return nil, err
		}
		var resp Response[T]
		err = json.Unmarshal(rbytes, &resp)
		if err != nil {
			return nil, err
		}
		return &resp, nil
	case []byte:
		var resp Response[T]
		err := json.Unmarshal(v, &resp)
		if err != nil {
			return nil, err
		}
		return &resp, nil
	default:
		return nil, fmt.Errorf("unsupported type: %T", val)
	}
}
