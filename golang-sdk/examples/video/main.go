package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"time"

	onethingai "wx-gitlab.xunlei.cn/computing_platform/onethingai-sdk/golang-sdk"
)

func main() {
	// Get API key from environment variable or use default
	apiKey := os.Getenv("ONETHINGAI_API_KEY")
	if apiKey == "" {
		// apiKey = "6c5cd6d9f92101f463709726fd2bbebf" // 正式环境 API Key
		apiKey = "fd36d0f69b6466e24491d78d80c124d2"
	}

	baseUrl := os.Getenv("ONETHINGAI_BASE_URL")
	if baseUrl == "" {
		// baseUrl = "https://api-model.onethingai.com/v2" // 正式环境 URL
		baseUrl = "http://api-model.onethingaidev.com/v2"
	}

	// Create client
	client, err := onethingai.NewClient(apiKey, onethingai.WithBaseURL(baseUrl))
	if err != nil {
		log.Fatalf("Failed to create client: %v", err)
	}
	defer client.Close()

	ctx := context.Background()
	fmt.Println("╔═══════════════════════════════════════════════════════════╗")
	fmt.Println("║         OneThing AI - Video Generation Examples          ║")
	fmt.Println("╚═══════════════════════════════════════════════════════════╝")
	fmt.Println()

	examples := []struct {
		name string
		fn   func(context.Context, *onethingai.Client) error
	}{
		// {"Basic Text-to-Video", example1TextToVideo},
		{"Image-to-Video", example2ImageToVideo},
		// {"Query-Video", example3QueryVideo},
	}

	for i, ex := range examples {
		if err := ex.fn(ctx, client); err != nil {
			log.Printf("❌ %s error: %v\n", ex.name, err)
		}
		if i < len(examples)-1 {
			fmt.Println()
		}
	}

	fmt.Println("\n✅ All video generation examples completed!")
}

func example1TextToVideo(ctx context.Context, client *onethingai.Client) error {
	fmt.Println("🎬 Example 1: Basic Text-to-Video")
	fmt.Println("─────────────────────────────────")

	req := &onethingai.VideoRequest{
		Model:   "sora-2",
		JobType: onethingai.VideoJobTypeText2Video,
		Prompt:  "A serene landscape with mountains and a river at sunset",
		Parameters: &onethingai.Parameters[onethingai.VideoOutputConfig]{
			OutputConfig: &onethingai.VideoOutputConfig{
				Height:   onethingai.IntPtr(1024),
				Width:    onethingai.IntPtr(1024),
				Duration: onethingai.IntPtr(3),
				Fps:      onethingai.IntPtr(24),
			},
		},
	}

	// 提交请求
	response, err := client.GenerateVideo(ctx, req)
	if err != nil {
		return fmt.Errorf("video generation failed: %w", err)
	}

	// 等待视频生成完成
	response, err = client.WaitForVideo(ctx, response.Data.JobID, &onethingai.PollingOptions{
		MaxAttempts: 100,
		Interval:    5 * time.Second,
		Timeout:     0,
		OnProgress: func(progress float64, status onethingai.Status) {
			log.Printf("progress:%.2f,status:%v", progress, status)
		},
	})
	if err != nil {
		return fmt.Errorf("video generation failed: %w", err)
	}

	videoData := response.Data
	fmt.Printf("✓ Job ID: %s\n", videoData.JobID)
	fmt.Printf("✓ Status: %s\n", videoData.Status)
	fmt.Printf("✓ Progress: %.1f%%\n", videoData.Progress*100)
	fmt.Printf("✓ Request ID: %s\n", response.RequestID)

	if videoData.Result != nil && len(videoData.Result.Data) > 0 {
		video := videoData.Result.Data[0]
		fmt.Printf("\n🎥 Generated Video:\n")
		fmt.Printf("  • URL: %s\n", video.GetURL())
		fmt.Printf("  • Duration: %ds\n", video.GetDuration())
		fmt.Printf("  • FPS: %d\n", video.GetFps())
	}

	return nil
}

func example2ImageToVideo(ctx context.Context, client *onethingai.Client) error {
	fmt.Println("🖼️  Example 2: Image-to-Video")
	fmt.Println("─────────────────────────────")

	req := &onethingai.VideoRequest{
		Model:   "sora-2",
		JobType: onethingai.VideoJobTypeText2Video,
		Prompt:  "the dog and penguin playing together",
		Parameters: &onethingai.Parameters[onethingai.VideoOutputConfig]{
			InputImages: []onethingai.InputImage{
				{
					URL: onethingai.StringPtr("https://gips2.baidu.com/it/u=195724436,3554684702&fm=3028&app=3028&f=JPEG&fmt=auto?w=1280&h=960"),
				},
				{
					URL: onethingai.StringPtr("https://gips1.baidu.com/it/u=3874647369,3220417986&fm=3028&app=3028&f=JPEG&fmt=auto?w=720&h=1280"),
				},
			},
			OutputConfig: &onethingai.VideoOutputConfig{
				Height:   onethingai.IntPtr(1024),
				Width:    onethingai.IntPtr(1024),
				Duration: onethingai.IntPtr(3),
				Fps:      onethingai.IntPtr(24),
			},
		},
	}

	// 提交请求
	response, err := client.GenerateVideo(ctx, req)
	if err != nil {
		return fmt.Errorf("video generation failed: %w", err)
	}

	// 等待视频生成完成
	response, err = client.WaitForVideo(ctx, response.Data.JobID, &onethingai.PollingOptions{
		MaxAttempts: 100,
		Interval:    5 * time.Second,
		Timeout:     0,
		OnProgress: func(progress float64, status onethingai.Status) {
			log.Printf("progress:%.2f,status:%v", progress, status)
		},
	})
	if err != nil {
		return fmt.Errorf("video generation failed: %w", err)
	}

	videoData := response.Data
	fmt.Printf("✓ Job Type: %s\n", onethingai.VideoJobTypeImage2Video)
	fmt.Printf("✓ Job ID: %s\n", videoData.JobID)

	if videoData.Result != nil && len(videoData.Result.Data) > 0 {
		video := videoData.Result.Data[0]
		fmt.Printf("\n🎥 Generated Video:\n")
		fmt.Printf("  • URL: %s\n", video.GetURL())
	}

	return nil
}
