package main

import (
	"context"
	"fmt"
	"log"
	"os"

	onethingai "wx-gitlab.xunlei.cn/computing_platform/onethingai-sdk/golang-sdk"
)

var (
	reqModel = "gpt-4o"
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
	fmt.Println("║         OneThing AI - Text Generation Examples           ║")
	fmt.Println("╚═══════════════════════════════════════════════════════════╝")
	fmt.Println()

	// Example 1: Chat Completion
	if err := example1ChatCompletion(ctx, client); err != nil {
		log.Printf("❌ Chat completion error: %v\n", err)
	}
	fmt.Println()

	// Example 2: Chat Completion Streaming
	if err := example2ChatCompletionStreaming(ctx, client); err != nil {
		log.Printf("❌ Chat completion streaming error: %v\n", err)
	}
	fmt.Println()

	// Example 3: Completions
	if err := example3Completions(ctx, client); err != nil {
		log.Printf("❌ Completions error: %v\n", err)
	}
	fmt.Println()

	// Example 4: Completions Streaming
	if err := example4CompletionsStreaming(ctx, client); err != nil {
		log.Printf("❌ Completions streaming error: %v\n", err)
	}
	fmt.Println()

	// Example 5: Responses
	if err := example5Responses(ctx, client); err != nil {
		log.Printf("❌ Responses error: %v\n", err)
	}
	fmt.Println()

	// Example 6: ResponsesStreaming
	if err := example6ResponsesStreaming(ctx, client); err != nil {
		log.Printf("❌ Responses streaming error: %v\n", err)
	}
	fmt.Println()

	// Example 7: Multi-turn Conversation
	if err := example7MultiTurnConversation(ctx, client); err != nil {
		log.Printf("❌ Multi-turn conversation error: %v\n", err)
	}
	fmt.Println()

	// Example 7: Generic Text Generation with Custom Parameters
	if err := example7CustomParameters(ctx, client); err != nil {
		log.Printf("❌ Custom parameters error: %v\n", err)
	}
	fmt.Println()

	// Example 8: Different Temperature Settings
	if err := example8TemperatureVariations(ctx, client); err != nil {
		log.Printf("❌ Temperature variations error: %v\n", err)
	}
	fmt.Println()

	fmt.Println("✅ All text generation examples completed!")
}

// Example 1: Basic Chat Completion
func example1ChatCompletion(ctx context.Context, client *onethingai.Client) error {
	fmt.Println("📝 Example 1: Basic Chat Completion")
	fmt.Println("───────────────────────────────────")

	request := map[string]interface{}{
		"model": reqModel,
		"messages": []map[string]interface{}{
			{
				"role":    "system",
				"content": "You are a helpful AI assistant.",
			},
			{
				"role":    "user",
				"content": "Explain quantum computing in one sentence.",
			},
		},
		"max_tokens":  100,
		"temperature": 0.7,
	}

	response, err := client.ChatCompletion(ctx, request)
	if err != nil {
		return fmt.Errorf("chat completion failed: %w", err)
	}

	fmt.Printf("✓ Request ID: %s\n", response.RequestID)
	fmt.Printf("✓ Response Code: %d\n", response.Code)

	if choices, ok := response.Data["choices"].([]interface{}); ok && len(choices) > 0 {
		if choice, ok := choices[0].(map[string]interface{}); ok {
			if message, ok := choice["message"].(map[string]interface{}); ok {
				if content, ok := message["content"].(string); ok {
					fmt.Printf("\n💬 Assistant: %s\n", content)
				}
			}
		}
	}

	return nil
}

// Example 2: Streaming Chat Completion
func example2ChatCompletionStreaming(ctx context.Context, client *onethingai.Client) error {
	fmt.Println("🌊 Example 2: Streaming Chat Completion")
	fmt.Println("───────────────────────────────────────")

	request := map[string]interface{}{
		"model": reqModel,
		"messages": []map[string]interface{}{
			{
				"role":    "user",
				"content": "Write a short poem about AI.",
			},
		},
		"max_tokens":  150,
		"temperature": 0.8,
	}

	reader, err := client.ChatCompletionStreaming(ctx, request)
	if err != nil {
		return fmt.Errorf("streaming failed: %w", err)
	}
	defer reader.Close()

	fmt.Print("\n💬 Assistant: ")

	for {
		chunk, err := reader.Next()
		if err != nil {
			break // EOF or error
		}

		if choices, ok := chunk["choices"].([]interface{}); ok && len(choices) > 0 {
			if choice, ok := choices[0].(map[string]interface{}); ok {
				if delta, ok := choice["delta"].(map[string]interface{}); ok {
					if content, ok := delta["content"].(string); ok {
						fmt.Print(content)
					}
				}
			}
		}
	}

	fmt.Println("\n\n✓ Streaming completed!")
	return nil
}

// Example 3: Text Completions
func example3Completions(ctx context.Context, client *onethingai.Client) error {
	fmt.Println("📄 Example 3: Text Completions")
	fmt.Println("──────────────────────────────")

	request := map[string]interface{}{
		"model":       reqModel,
		"prompt":      "The future of artificial intelligence is",
		"max_tokens":  100,
		"temperature": 0.7,
	}

	response, err := client.Completions(ctx, request)
	if err != nil {
		return fmt.Errorf("completions failed: %w", err)
	}

	fmt.Printf("✓ Request ID: %s\n", response.RequestID)

	if choices, ok := response.Data["choices"].([]interface{}); ok && len(choices) > 0 {
		if choice, ok := choices[0].(map[string]interface{}); ok {
			var text string
			if t, ok := choice["text"].(string); ok {
				text = t
			} else if message, ok := choice["message"].(map[string]interface{}); ok {
				if content, ok := message["content"].(string); ok {
					text = content
				}
			}
			fmt.Printf("\n📝 Completed: %s\n", text)
		}
	}

	return nil
}

// Example 4: Completions Streaming
func example4CompletionsStreaming(ctx context.Context, client *onethingai.Client) error {
	fmt.Println("🌊 Example 4: Completions Streaming")
	fmt.Println("───────────────────────────────────")

	request := map[string]interface{}{
		"model":       reqModel,
		"prompt":      "Once upon a time in a digital world,",
		"max_tokens":  150,
		"temperature": 0.9,
	}

	reader, err := client.CompletionsStreaming(ctx, request)
	if err != nil {
		return fmt.Errorf("streaming completions failed: %w", err)
	}
	defer reader.Close()

	fmt.Print("\n📖 Story: ")

	for {
		chunk, err := reader.Next()
		if err != nil {
			break
		}

		if choices, ok := chunk["choices"].([]interface{}); ok && len(choices) > 0 {
			if choice, ok := choices[0].(map[string]interface{}); ok {
				if delta, ok := choice["delta"].(map[string]interface{}); ok {
					if content, ok := delta["content"].(string); ok {
						fmt.Print(content)
					}
				}
			}
		}
	}

	fmt.Println("\n\n✓ Story generation completed!")
	return nil
}

// Example 5: Responses
func example5Responses(ctx context.Context, client *onethingai.Client) error {
	fmt.Println("💡 Example 5: Responses")
	fmt.Println("────────────────────────────")

	request := map[string]interface{}{
		"model": reqModel,
		"input": "What are the benefits of renewable energy?",
	}

	response, err := client.Responses(ctx, request)
	if err != nil {
		return fmt.Errorf("responses failed: %w", err)
	}

	fmt.Printf("✓ Request ID: %s\n", response.RequestID)
	log.Printf("Response:%v", response.Data)

	if choices, ok := response.Data["choices"].([]interface{}); ok && len(choices) > 0 {
		if choice, ok := choices[0].(map[string]interface{}); ok {
			var text string
			if t, ok := choice["text"].(string); ok {
				text = t
			} else if message, ok := choice["message"].(map[string]interface{}); ok {
				if content, ok := message["content"].(string); ok {
					text = content
				}
			}
			fmt.Printf("\n💭 Response: %s\n", text)
		}
	}

	return nil
}

func example6ResponsesStreaming(ctx context.Context, client *onethingai.Client) error {
	fmt.Println("🌊 Example 6: Responses Streaming")
	fmt.Println("────────────────────────────")

	request := map[string]interface{}{
		"model": reqModel,
		"input": "What are the benefits of renewable energy?",
	}

	reader, err := client.ResponsesStreaming(ctx, request)
	if err != nil {
		return fmt.Errorf("streaming responses failed: %w", err)
	}
	defer reader.Close()

	fmt.Print("\n📖 Story: ")

	for {
		chunk, err := reader.Next()
		if err != nil {
			break
		}

		log.Printf("Chunk:%v", chunk)

	}

	return nil
}

// Example 7: Multi-turn Conversation
func example7MultiTurnConversation(ctx context.Context, client *onethingai.Client) error {
	fmt.Println("💬 Example 7: Multi-turn Conversation")
	fmt.Println("─────────────────────────────────────")

	// Simulate a conversation history
	messages := []map[string]interface{}{
		{
			"role":    "system",
			"content": "You are a helpful programming tutor.",
		},
		{
			"role":    "user",
			"content": "What is recursion?",
		},
		{
			"role":    "assistant",
			"content": "Recursion is when a function calls itself to solve a problem by breaking it down into smaller subproblems.",
		},
		{
			"role":    "user",
			"content": "Can you give me a simple example in Python?",
		},
	}

	request := map[string]interface{}{
		"model":       reqModel,
		"messages":    messages,
		"max_tokens":  200,
		"temperature": 0.7,
	}

	response, err := client.ChatCompletion(ctx, request)
	if err != nil {
		return fmt.Errorf("multi-turn conversation failed: %w", err)
	}

	fmt.Println("📚 Conversation Context:")
	for i, msg := range messages {
		role := msg["role"].(string)
		content := msg["content"].(string)
		if role == "system" {
			fmt.Printf("  [System] %s\n", content)
		} else if role == "user" {
			fmt.Printf("  👤 User: %s\n", content)
		} else {
			fmt.Printf("  🤖 Assistant: %s\n", content)
		}
		if i < len(messages)-1 {
			fmt.Println()
		}
	}

	if choices, ok := response.Data["choices"].([]interface{}); ok && len(choices) > 0 {
		if choice, ok := choices[0].(map[string]interface{}); ok {
			if message, ok := choice["message"].(map[string]interface{}); ok {
				if content, ok := message["content"].(string); ok {
					fmt.Printf("\n🤖 Assistant: %s\n", content)
				}
			}
		}
	}

	return nil
}

// Example 7: Generic Text Generation with Custom Parameters
func example7CustomParameters(ctx context.Context, client *onethingai.Client) error {
	fmt.Println("⚙️  Example 7: Custom Parameters")
	fmt.Println("────────────────────────────────")

	request := map[string]interface{}{
		"model":    reqModel,
		"job_type": onethingai.TextJobTypeChatCompletions,
		"messages": []map[string]interface{}{
			{
				"role":    "user",
				"content": "Write a creative product name for a smart coffee maker.",
			},
		},
		"max_tokens":        50,
		"temperature":       1.0, // High creativity
		"top_p":             0.9,
		"frequency_penalty": 0.5,
		"presence_penalty":  0.5,
	}

	response, err := client.GenerateText(ctx, request)
	if err != nil {
		return fmt.Errorf("custom parameters generation failed: %w", err)
	}

	fmt.Println("⚙️  Custom Parameters:")
	fmt.Printf("  • Temperature: %.1f (high creativity)\n", request["temperature"])
	fmt.Printf("  • Top P: %.1f\n", request["top_p"])
	fmt.Printf("  • Frequency Penalty: %.1f\n", request["frequency_penalty"])
	fmt.Printf("  • Presence Penalty: %.1f\n", request["presence_penalty"])

	if choices, ok := response.Data["choices"].([]interface{}); ok && len(choices) > 0 {
		if choice, ok := choices[0].(map[string]interface{}); ok {
			if message, ok := choice["message"].(map[string]interface{}); ok {
				if content, ok := message["content"].(string); ok {
					fmt.Printf("\n💡 Generated Name: %s\n", content)
				}
			}
		}
	}

	return nil
}

// Example 8: Different Temperature Settings
func example8TemperatureVariations(ctx context.Context, client *onethingai.Client) error {
	fmt.Println("🌡️  Example 8: Temperature Variations")
	fmt.Println("─────────────────────────────────────")

	prompt := "Describe the color blue in one sentence."
	temperatures := []float64{0.2, 0.7, 1.2}

	for i, temp := range temperatures {
		fmt.Printf("\n🌡️  Temperature: %.1f\n", temp)

		request := map[string]interface{}{
			"model": reqModel,
			"messages": []map[string]interface{}{
				{
					"role":    "user",
					"content": prompt,
				},
			},
			"max_tokens":  60,
			"temperature": temp,
		}

		response, err := client.ChatCompletion(ctx, request)
		if err != nil {
			log.Printf("Temperature %.1f failed: %v", temp, err)
			continue
		}

		if choices, ok := response.Data["choices"].([]interface{}); ok && len(choices) > 0 {
			if choice, ok := choices[0].(map[string]interface{}); ok {
				if message, ok := choice["message"].(map[string]interface{}); ok {
					if content, ok := message["content"].(string); ok {
						fmt.Printf("💭 Response: %s\n", content)
					}
				}
			}
		}

		if i < len(temperatures)-1 {
			fmt.Println()
		}
	}

	fmt.Println("\n✓ Temperature comparison completed!")
	return nil
}
