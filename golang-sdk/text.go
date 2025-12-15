package onethingai

import (
	"context"
	"fmt"
)

// validateTextJobType validates the job_type for text generation
func validateTextJobType(jobType interface{}) error {
	if jobType == "" || jobType == nil {
		return nil // Will use default
	}

	jt, ok := jobType.(TextJobType)
	if !ok {
		// Try string conversion
		if str, ok := jobType.(string); ok {
			jt = TextJobType(str)
		} else {
			return fmt.Errorf("invalid job_type type: %T", jobType)
		}
	}

	if jt != TextJobTypeCompletions && jt != TextJobTypeChatCompletions && jt != TextJobTypeResponses {
		return fmt.Errorf("invalid job_type: %v", jt)
	}
	return nil
}

// validateTextRequest validates text generation request
func validateTextRequest(req map[string]interface{}, jobType TextJobType, stream bool) error {
	if req == nil {
		return fmt.Errorf("request cannot be nil")
	}

	// Validate model
	if model, ok := req["model"]; !ok || model == "" {
		return fmt.Errorf("model is required")
	}

	// Set job_type
	req["job_type"] = jobType

	// Validate job_type
	if err := validateTextJobType(req["job_type"]); err != nil {
		return err
	}

	// Set stream
	if stream {
		req["stream"] = true
	} else {
		delete(req, "stream")
	}

	return nil
}

// ChatCompletion performs chat completion
func (c *Client) ChatCompletion(ctx context.Context, req map[string]interface{}) (*TextResponse, error) {
	if err := validateTextRequest(req, TextJobTypeChatCompletions, false); err != nil {
		return nil, err
	}
	return c.generateText(ctx, req)
}

// Completions performs text completions
func (c *Client) Completions(ctx context.Context, req map[string]interface{}) (*TextResponse, error) {
	if err := validateTextRequest(req, TextJobTypeCompletions, false); err != nil {
		return nil, err
	}
	return c.generateText(ctx, req)
}

// Responses performs text responses
func (c *Client) Responses(ctx context.Context, req map[string]interface{}) (*TextResponse, error) {
	if err := validateTextRequest(req, TextJobTypeResponses, false); err != nil {
		return nil, err
	}
	return c.generateText(ctx, req)
}

// GenerateText generates text (non-streaming)
func (c *Client) GenerateText(ctx context.Context, req map[string]interface{}) (*TextResponse, error) {
	if req == nil {
		return nil, fmt.Errorf("request cannot be nil")
	}

	// Validate required fields
	if model, ok := req["model"]; !ok || model == "" {
		return nil, fmt.Errorf("model is required")
	}

	// Set default job_type if not provided
	if _, ok := req["job_type"]; !ok {
		req["job_type"] = TextJobTypeChatCompletions
	}

	// Validate job_type
	if err := validateTextJobType(req["job_type"]); err != nil {
		return nil, err
	}

	// Ensure stream is not set for non-streaming
	delete(req, "stream")

	return c.generateText(ctx, req)
}

// generateText is the internal method for text generation
func (c *Client) generateText(ctx context.Context, req map[string]interface{}) (*TextResponse, error) {
	var respMap map[string]interface{}
	err := c.doRequest(ctx, "POST", "/generation", req, &respMap)
	if err != nil {
		return nil, err
	}
	return NewTextResponse(respMap)
}

// ChatCompletionStreaming performs chat completion with streaming
func (c *Client) ChatCompletionStreaming(ctx context.Context, req map[string]interface{}) (*TextStreamReader, error) {
	if err := validateTextRequest(req, TextJobTypeChatCompletions, true); err != nil {
		return nil, err
	}
	return c.generateTextStream(ctx, req)
}

// CompletionsStreaming performs text completions with streaming
func (c *Client) CompletionsStreaming(ctx context.Context, req map[string]interface{}) (*TextStreamReader, error) {
	if err := validateTextRequest(req, TextJobTypeCompletions, true); err != nil {
		return nil, err
	}
	return c.generateTextStream(ctx, req)
}

// ResponsesStreaming performs text responses with streaming
func (c *Client) ResponsesStreaming(ctx context.Context, req map[string]interface{}) (*TextStreamReader, error) {
	if err := validateTextRequest(req, TextJobTypeResponses, true); err != nil {
		return nil, err
	}
	return c.generateTextStream(ctx, req)
}

// GenerateTextStream generates text with streaming
func (c *Client) GenerateTextStream(ctx context.Context, req map[string]interface{}) (*TextStreamReader, error) {
	if req == nil {
		return nil, fmt.Errorf("request cannot be nil")
	}

	// Validate required fields
	if model, ok := req["model"]; !ok || model == "" {
		return nil, fmt.Errorf("model is required")
	}

	// Set default job_type if not provided
	if _, ok := req["job_type"]; !ok {
		req["job_type"] = TextJobTypeChatCompletions
	}

	// Validate job_type
	if err := validateTextJobType(req["job_type"]); err != nil {
		return nil, err
	}

	// Enable streaming
	req["stream"] = true

	return c.generateTextStream(ctx, req)
}

// generateTextStream is the internal method for streaming text generation
func (c *Client) generateTextStream(ctx context.Context, req map[string]interface{}) (*TextStreamReader, error) {
	resp, err := c.doStreamRequest(ctx, "POST", "/generation", req)
	if err != nil {
		return nil, err
	}
	return NewTextStreamReader(ctx, resp), nil
}
