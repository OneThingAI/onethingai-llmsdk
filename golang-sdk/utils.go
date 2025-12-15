package onethingai

import (
	"encoding/base64"
	"fmt"
	"io"
	"os"
	"strings"
)

// Helper functions for SDK users

// ==================== Image Helpers ====================

// URLToInputImage creates an InputImage from a URL
func URLToInputImage(url string) InputImage {
	return InputImage{URL: &url}
}

// B64ToInputImage creates an InputImage from base64 data
func B64ToInputImage(b64 string) InputImage {
	return InputImage{B64JSON: &b64}
}

// FileToInputImage reads a file and converts it to base64 InputImage
func FileToInputImage(filePath string) (InputImage, error) {
	data, err := os.ReadFile(filePath)
	if err != nil {
		return InputImage{}, fmt.Errorf("failed to read file: %w", err)
	}

	// Detect content type based on file extension
	contentType := detectContentType(filePath)

	// Encode to base64 with data URL prefix
	b64 := fmt.Sprintf("data:%s;base64,%s", contentType, base64.StdEncoding.EncodeToString(data))

	return InputImage{B64JSON: &b64}, nil
}

// ReaderToInputImage reads from an io.Reader and converts it to base64 InputImage
func ReaderToInputImage(reader io.Reader, contentType string) (InputImage, error) {
	data, err := io.ReadAll(reader)
	if err != nil {
		return InputImage{}, fmt.Errorf("failed to read data: %w", err)
	}

	// Encode to base64 with data URL prefix
	b64 := fmt.Sprintf("data:%s;base64,%s", contentType, base64.StdEncoding.EncodeToString(data))

	return InputImage{B64JSON: &b64}, nil
}

// detectContentType detects content type from file extension
func detectContentType(filePath string) string {
	ext := strings.ToLower(filePath[strings.LastIndex(filePath, ".")+1:])

	switch ext {
	case "jpg", "jpeg":
		return "image/jpeg"
	case "png":
		return "image/png"
	case "gif":
		return "image/gif"
	case "webp":
		return "image/webp"
	case "bmp":
		return "image/bmp"
	default:
		return "image/jpeg" // default
	}
}

// ==================== Video Helpers ====================

// URLToInputVideo creates an InputVideo from a URL
func URLToInputVideo(url string) InputVideo {
	return InputVideo{URL: &url}
}

// ==================== Size Helpers ====================

// Common image sizes
var (
	Size256x256   = Size{Width: 256, Height: 256}
	Size512x512   = Size{Width: 512, Height: 512}
	Size1024x1024 = Size{Width: 1024, Height: 1024}
	Size1024x1792 = Size{Width: 1024, Height: 1792}
	Size1792x1024 = Size{Width: 1792, Height: 1024}

	// Video sizes
	Size1280x720  = Size{Width: 1280, Height: 720}  // 720p
	Size1920x1080 = Size{Width: 1920, Height: 1080} // 1080p
	Size2560x1440 = Size{Width: 2560, Height: 1440} // 1440p
	Size3840x2160 = Size{Width: 3840, Height: 2160} // 4K
)

// Size represents dimensions
type Size struct {
	Width  int
	Height int
}

// ==================== Request Builders ====================

// IntPtr returns a pointer to an int
func IntPtr(i int) *int {
	return &i
}

// StringPtr returns a pointer to a string
func StringPtr(s string) *string {
	return &s
}

// BoolPtr returns a pointer to a bool
func BoolPtr(b bool) *bool {
	return &b
}

// ResponseFormatPtr returns a pointer to ResponseFormat
func ResponseFormatPtr(rf ResponseFormat) *ResponseFormat {
	return &rf
}

// ImageStylePtr returns a pointer to ImageStyle
func ImageStylePtr(style ImageStyle) *ImageStyle {
	return &style
}

// ==================== Validation Helpers ====================

// ValidateSize validates image/video dimensions
func ValidateSize(width, height int) error {
	if width <= 0 || height <= 0 {
		return NewValidationError("size", "width and height must be positive")
	}

	if width > 4096 || height > 4096 {
		return NewValidationError("size", "width and height cannot exceed 4096")
	}

	return nil
}

// ValidateN validates the number of outputs
func ValidateN(n int, maxN int) error {
	if n < 1 {
		return NewValidationError("n", "n must be at least 1")
	}

	if n > maxN {
		return NewValidationError("n", fmt.Sprintf("n cannot exceed %d", maxN))
	}

	return nil
}

// ValidateModel validates model name
func ValidateModel(model string) error {
	if model == "" {
		return NewValidationError("model", "model is required")
	}

	return nil
}

// ValidatePrompt validates prompt
func ValidatePrompt(prompt string) error {
	if prompt == "" {
		return NewValidationError("prompt", "prompt is required")
	}

	if len(prompt) > 10000 {
		return NewValidationError("prompt", "prompt is too long (max 10000 characters)")
	}

	return nil
}

// ==================== Response Helpers ====================

// GetFirstImage returns the first image from a response
func GetFirstImage(response *ImageDataResponse) (*ImageResult, error) {
	if response == nil || response.Result == nil || len(response.Result.Data) == 0 {
		return nil, fmt.Errorf("no images in response")
	}

	return &response.Result.Data[0], nil
}

// GetFirstVideo returns the first video from a response
func GetFirstVideo(response *VideoDataResponse) (*VideoResult, error) {
	if response == nil || response.Result == nil || len(response.Result.Data) == 0 {
		return nil, fmt.Errorf("no videos in response")
	}

	return &response.Result.Data[0], nil
}

// GetAllImageURLs returns all image URLs from a response
func GetAllImageURLs(response *ImageDataResponse) []string {
	if response == nil || response.Result == nil {
		return []string{}
	}

	urls := make([]string, 0, len(response.Result.Data))
	for _, img := range response.Result.Data {
		if img.URL != nil {
			urls = append(urls, *img.URL)
		}
	}

	return urls
}

// GetAllVideoURLs returns all video URLs from a response
func GetAllVideoURLs(response *VideoDataResponse) []string {
	if response == nil || response.Result == nil {
		return []string{}
	}

	urls := make([]string, 0, len(response.Result.Data))
	for _, video := range response.Result.Data {
		if video.URL != nil {
			urls = append(urls, *video.URL)
		}
	}

	return urls
}

// ==================== Debug Helpers ====================

// DebugRequest returns a string representation of a request for debugging
func DebugRequest(req interface{}) string {
	return fmt.Sprintf("%+v", req)
}

// DebugResponse returns a string representation of a response for debugging
func DebugResponse(resp interface{}) string {
	return fmt.Sprintf("%+v", resp)
}
