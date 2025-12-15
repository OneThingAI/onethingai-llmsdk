package main

import (
	"context"
	"fmt"
	"log"
	"os"

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
	fmt.Println("║         OneThing AI - Image Generation Examples          ║")
	fmt.Println("╚═══════════════════════════════════════════════════════════╝")
	fmt.Println()

	examples := []struct {
		name string
		fn   func(context.Context, *onethingai.Client) error
	}{
		{"Basic Image Generation", example1BasicImageGeneration},
		{"Image Generation Streaming ", example2ImageGenerationStreaming},
		{"Image Editing", example3ImageEditing},
		{"Image Editing Streaming", example4ImageEditingStreaming},
		{"Multi Image Editing", example5MultiImageEditing},
	}

	for i, ex := range examples {
		if err := ex.fn(ctx, client); err != nil {
			log.Printf("❌ %s error: %v\n", ex.name, err)
		}
		if i < len(examples)-1 {
			fmt.Println()
		}
	}

	fmt.Println("\n✅ All image generation examples completed!")
}

func example1BasicImageGeneration(ctx context.Context, client *onethingai.Client) error {
	fmt.Println("🎨 Example 1: Basic Sync Image Generation")
	fmt.Println("─────────────────────────────────────────")

	req := &onethingai.ImageRequest{
		Model:   "wan2.5-image-preview",
		JobType: onethingai.ImageJobTypeGeneration,
		Prompt:  "A serene landscape with mountains and a river at sunset",
		Parameters: &onethingai.Parameters[onethingai.ImageOutputConfig]{
			OutputConfig: &onethingai.ImageOutputConfig{
				Height:         onethingai.IntPtr(1024),
				Width:          onethingai.IntPtr(1024),
				ResponseFormat: onethingai.ResponseFormatPtr(onethingai.ResponseFormatURL),
			},
		},
	}

	response, err := client.GenerateImage(ctx, req)
	if err != nil {
		return fmt.Errorf("image generation failed: %w", err)
	}

	imgData := response.Data
	fmt.Printf("✓ Job ID: %s\n", imgData.JobID)
	fmt.Printf("✓ Status: %s\n", imgData.Status)
	fmt.Printf("✓ Request ID: %s\n", response.RequestID)

	if imgData.Result != nil && len(imgData.Result.Data) > 0 {
		for i, img := range imgData.Result.Data {
			fmt.Printf("\n📸 Image %d:\n", i+1)
			fmt.Printf("  • URL: %s\n", img.GetURL())
			fmt.Printf("  • Width: %s\n", img.GetB64JSON())
			fmt.Printf("  • Index: %d\n", img.Index)
		}
	}

	return nil
}

func example2ImageGenerationStreaming(ctx context.Context, client *onethingai.Client) error {
	fmt.Println("🌊 Example 2: Streaming Image Generation")
	fmt.Println("────────────────────────────────────────")

	req := &onethingai.ImageRequest{
		Model:   "doubao-seedream-4-0-250828",
		Stream:  onethingai.BoolPtr(true),
		JobType: onethingai.ImageJobTypeGeneration,
		Prompt:  "A serene landscape with mountains and a river at sunset",
		Parameters: &onethingai.Parameters[onethingai.ImageOutputConfig]{
			OutputConfig: &onethingai.ImageOutputConfig{
				Height:         onethingai.IntPtr(1024),
				Width:          onethingai.IntPtr(1024),
				ResponseFormat: onethingai.ResponseFormatPtr(onethingai.ResponseFormatURL),
			},
		},
	}

	reader, err := client.GenerateImageStream(ctx, req)
	if err != nil {
		return fmt.Errorf("streaming failed: %w", err)
	}
	defer reader.Close()

	fmt.Println("\n🎬 Processing stream events...")

	for {
		event, err := reader.Next()
		if err != nil {
			break
		}

		switch event.Type {
		case onethingai.EventTypeProgress:
			fmt.Printf("  📊 Progress event received\n")
		case onethingai.EventTypePartialResult:
			fmt.Printf("  🖼️  Partial result: Index %d\n", event.Data.Index)
			if event.Data.URL != nil {
				fmt.Printf("     URL: %s\n", event.Data.GetURL())
				fmt.Printf("     B64JSON: %s\n", event.Data.GetB64JSON())
			}
		case onethingai.EventTypeDone:
			fmt.Println("  ✅ Generation completed!")
		case onethingai.EventTypeError:
			fmt.Printf("  ❌ Error: %v\n", event.Error)
		}
	}

	return nil
}

func example3ImageEditing(ctx context.Context, client *onethingai.Client) error {
	fmt.Println("✏️  Example 3: Image Editing")
	fmt.Println("───────────────────────────")

	req := &onethingai.ImageRequest{
		Model:   "doubao-seedream-4-0-250828",
		JobType: onethingai.ImageJobTypeEdit,
		Prompt:  "change the dog to a cat",
		Parameters: &onethingai.Parameters[onethingai.ImageOutputConfig]{
			OutputConfig: &onethingai.ImageOutputConfig{
				Height:         onethingai.IntPtr(1024),
				Width:          onethingai.IntPtr(1024),
				ResponseFormat: onethingai.ResponseFormatPtr(onethingai.ResponseFormatURL),
			},
			InputImages: []onethingai.InputImage{
				{
					URL: onethingai.StringPtr("https://gips2.baidu.com/it/u=195724436,3554684702&fm=3028&app=3028&f=JPEG&fmt=auto?w=1280&h=960"),
				},
			},
		},
	}

	response, err := client.GenerateImage(ctx, req)
	if err != nil {
		return fmt.Errorf("image editing failed: %w", err)
	}

	imgData := response.Data
	fmt.Printf("✓ Job Type: %s\n", onethingai.ImageJobTypeEdit)
	fmt.Printf("✓ Job ID: %s\n", imgData.JobID)

	if imgData.Result != nil && len(imgData.Result.Data) > 0 {
		for i, img := range imgData.Result.Data {
			fmt.Printf("\n📸 Image %d:\n", i+1)
			fmt.Printf("  • URL: %s\n", img.GetURL())
			fmt.Printf("  • B64JSON: %s\n", img.GetB64JSON())
		}
	}

	return nil
}

func example4ImageEditingStreaming(ctx context.Context, client *onethingai.Client) error {
	fmt.Println("✏️  Example 4: Image Editing Streaming")
	fmt.Println("───────────────────────────")

	req := &onethingai.ImageRequest{
		Model:   "doubao-seedream-4-0-250828",
		Stream:  onethingai.BoolPtr(true),
		JobType: onethingai.ImageJobTypeEdit,
		Prompt:  "change the dog to a cat",
		Parameters: &onethingai.Parameters[onethingai.ImageOutputConfig]{
			OutputConfig: &onethingai.ImageOutputConfig{
				Height:         onethingai.IntPtr(1024),
				Width:          onethingai.IntPtr(1024),
				ResponseFormat: onethingai.ResponseFormatPtr(onethingai.ResponseFormatURL),
			},
			InputImages: []onethingai.InputImage{
				{
					URL: onethingai.StringPtr("https://gips2.baidu.com/it/u=195724436,3554684702&fm=3028&app=3028&f=JPEG&fmt=auto?w=1280&h=960"),
				},
			},
		},
	}

	reader, err := client.GenerateImageStream(ctx, req)
	if err != nil {
		return fmt.Errorf("streaming failed: %w", err)
	}
	defer reader.Close()

	fmt.Println("\n🎬 Processing stream events...")

	for {
		event, err := reader.Next()
		if err != nil {
			break
		}

		switch event.Type {
		case onethingai.EventTypeProgress:
			fmt.Printf("  📊 Progress event received\n")
		case onethingai.EventTypePartialResult:
			fmt.Printf("  🖼️  Partial result: Index %d\n", event.Data.Index)
			if event.Data.URL != nil {
				fmt.Printf("     URL: %s\n", event.Data.GetURL())
				fmt.Printf("     B64JSON: %s\n", event.Data.GetB64JSON())
			}
		case onethingai.EventTypeDone:
			fmt.Println("  ✅ Generation completed!")
		case onethingai.EventTypeError:
			fmt.Printf("  ❌ Error: %v\n", event.Error)
		}
	}

	return nil
}

func example5MultiImageEditing(ctx context.Context, client *onethingai.Client) error {
	fmt.Println("✏️  Example 5: Multi Image Editing")
	fmt.Println("───────────────────────────")

	imageURL := "https://example.com/source-image.jpg"

	req := &onethingai.ImageRequest{
		Model:   "gemini-3-pro-image",
		JobType: onethingai.ImageJobTypeEdit,
		Prompt:  "change the dog to a cat, and the penguin play with the cat ",
		Parameters: &onethingai.Parameters[onethingai.ImageOutputConfig]{
			OutputConfig: &onethingai.ImageOutputConfig{
				Height:         onethingai.IntPtr(1024),
				Width:          onethingai.IntPtr(1024),
				ResponseFormat: onethingai.ResponseFormatPtr(onethingai.ResponseFormatURL),
			},
			InputImages: []onethingai.InputImage{
				{
					URL: onethingai.StringPtr("https://gips2.baidu.com/it/u=195724436,3554684702&fm=3028&app=3028&f=JPEG&fmt=auto?w=1280&h=960"),
				},
				{
					URL: onethingai.StringPtr("https://gips1.baidu.com/it/u=3874647369,3220417986&fm=3028&app=3028&f=JPEG&fmt=auto?w=720&h=1280"),
				},
			},
		},
	}

	response, err := client.GenerateImage(ctx, req)
	if err != nil {
		return fmt.Errorf("image editing failed: %w", err)
	}

	imgData := response.Data
	fmt.Printf("✓ Job Type: %s\n", onethingai.ImageJobTypeEdit)
	fmt.Printf("✓ Job ID: %s\n", imgData.JobID)
	fmt.Printf("✓ Source Image: %s\n", imageURL)

	if imgData.Result != nil && len(imgData.Result.Data) > 0 {
		for i, img := range imgData.Result.Data {
			fmt.Printf("\n📸 Image %d:\n", i+1)
			fmt.Printf("  • URL: %s\n", img.GetURL())
			fmt.Printf("  • B64JSON: %s\n", img.GetB64JSON())
		}
	}

	return nil
}
