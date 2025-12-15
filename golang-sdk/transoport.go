package onethingai

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// Transport handles HTTP communication with the API
type Transport struct {
	client     *http.Client
	baseURL    string
	apiKey     string
	maxRetries int
	headers    map[string]string
}

// New creates a new transport instance
func New(client *http.Client, cfg *Config) *Transport {
	return &Transport{
		client:     client,
		baseURL:    cfg.BaseURL,
		apiKey:     cfg.APIKey,
		maxRetries: cfg.MaxRetries,
		headers:    cfg.Headers,
	}
}

// DoRequest performs an HTTP request with retry logic
func (t *Transport) DoRequest(ctx context.Context, method, path string, body interface{}, result interface{}) error {
	var lastErr error

	for attempt := 0; attempt <= t.maxRetries; attempt++ {
		if attempt > 0 {
			// Exponential backoff
			backoff := time.Duration(attempt) * time.Second
			select {
			case <-ctx.Done():
				return ctx.Err()
			case <-time.After(backoff):
			}
		}

		err := t.doRequestOnce(ctx, method, path, body, result)
		if err == nil {
			return nil
		}

		// Check if error is retryable
		if httpErr, ok := err.(*HTTPError); ok {
			// Don't retry client errors (4xx) except 429
			if httpErr.StatusCode >= 400 && httpErr.StatusCode < 500 && httpErr.StatusCode != 429 {
				return err
			}
		}

		lastErr = err
	}

	return fmt.Errorf("max retries exceeded: %w", lastErr)
}

// doRequestOnce performs a single HTTP request
func (t *Transport) doRequestOnce(ctx context.Context, method, path string, body interface{}, result interface{}) error {
	url := t.baseURL + path

	// Prepare request body
	var reqBody io.Reader
	if body != nil {
		jsonData, err := json.Marshal(body)
		if err != nil {
			return fmt.Errorf("failed to marshal request body: %w", err)
		}
		reqBody = bytes.NewReader(jsonData)
	}

	// Create request
	req, err := http.NewRequestWithContext(ctx, method, url, reqBody)
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	// Set headers
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+t.apiKey)
	req.Header.Set("User-Agent", "onethingai-go-sdk/1.0.0")

	// Add custom headers
	for key, value := range t.headers {
		req.Header.Set(key, value)
	}

	// Execute request
	resp, err := t.client.Do(req)
	if err != nil {
		return fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	// Read response body
	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("failed to read response body: %w", err)
	}

	// Check for error status codes
	if resp.StatusCode >= 400 {
		var errorMsg string

		// Try to parse error message from JSON
		var errResp struct {
			Error struct {
				Message string `json:"message"`
			} `json:"error"`
			Message string `json:"message"`
		}

		if err := json.Unmarshal(respBody, &errResp); err == nil {
			if errResp.Error.Message != "" {
				errorMsg = errResp.Error.Message
			} else if errResp.Message != "" {
				errorMsg = errResp.Message
			}
		}

		if errorMsg == "" {
			errorMsg = string(respBody)
		}

		return &HTTPError{
			StatusCode: resp.StatusCode,
			Message:    errorMsg,
			Body:       string(respBody),
		}
	}

	// Parse successful response
	if result != nil {
		if err := json.Unmarshal(respBody, result); err != nil {
			return fmt.Errorf("failed to unmarshal response: %w", err)
		}
	}

	return nil
}

// DoStreamRequest performs a streaming HTTP request
func (t *Transport) DoStreamRequest(ctx context.Context, method, path string, body interface{}) (*http.Response, error) {
	url := t.baseURL + path

	// Prepare request body
	var reqBody io.Reader
	if body != nil {
		jsonData, err := json.Marshal(body)
		if err != nil {
			return nil, fmt.Errorf("failed to marshal request body: %w", err)
		}
		reqBody = bytes.NewReader(jsonData)
	}

	// Create request
	req, err := http.NewRequestWithContext(ctx, method, url, reqBody)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	// Set headers
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+t.apiKey)
	req.Header.Set("Accept", "text/event-stream")
	req.Header.Set("Cache-Control", "no-cache")
	req.Header.Set("Connection", "keep-alive")
	req.Header.Set("User-Agent", "onethingai-go-sdk/1.0.0")

	// Add custom headers
	for key, value := range t.headers {
		req.Header.Set(key, value)
	}

	// Execute request
	resp, err := t.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to execute request: %w", err)
	}

	// Check for error status codes
	if resp.StatusCode >= 400 {
		defer resp.Body.Close()

		respBody, err := io.ReadAll(resp.Body)
		if err != nil {
			return nil, fmt.Errorf("HTTP %d: failed to read error response", resp.StatusCode)
		}

		var errorMsg string
		var errResp struct {
			Error struct {
				Message string `json:"message"`
			} `json:"error"`
			Message string `json:"message"`
		}

		if err := json.Unmarshal(respBody, &errResp); err == nil {
			if errResp.Error.Message != "" {
				errorMsg = errResp.Error.Message
			} else if errResp.Message != "" {
				errorMsg = errResp.Message
			}
		}

		if errorMsg == "" {
			errorMsg = string(respBody)
		}

		return nil, &HTTPError{
			StatusCode: resp.StatusCode,
			Message:    errorMsg,
			Body:       string(respBody),
		}
	}

	return resp, nil
}
