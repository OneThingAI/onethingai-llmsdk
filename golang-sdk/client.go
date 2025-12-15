package onethingai

import (
	"fmt"
	"net/http"
	"time"
)

const (
	DefaultBaseURL       = "https://api-model.onethingai.com/v2"
	DefaultTimeout       = 60 * time.Second
	DefaultMaxRetries    = 3
	DefaultPollingPeriod = 2 * time.Second
)

// Client is the main SDK client
type Client struct {
	config    *Config
	transport *Transport
}

// Config holds the SDK configuration
type Config struct {
	// API Key for authentication
	APIKey string

	// Base URL for the API
	BaseURL string

	// HTTP timeout
	Timeout time.Duration

	// Maximum number of retries for failed requests
	MaxRetries int

	// Custom HTTP client (optional)
	HTTPClient *http.Client

	// Polling period for async jobs
	PollingPeriod time.Duration

	// Custom headers
	Headers map[string]string
}

// NewClient creates a new OneThing AI SDK client
func NewClient(apiKey string, opts ...ClientOption) (*Client, error) {
	if apiKey == "" {
		return nil, fmt.Errorf("API key is required")
	}

	config := &Config{
		APIKey:        apiKey,
		BaseURL:       DefaultBaseURL,
		Timeout:       DefaultTimeout,
		MaxRetries:    DefaultMaxRetries,
		PollingPeriod: DefaultPollingPeriod,
		Headers:       make(map[string]string),
	}

	// Apply options
	for _, opt := range opts {
		opt(config)
	}

	// Create HTTP client if not provided
	httpClient := config.HTTPClient
	if httpClient == nil {
		httpClient = &http.Client{
			Timeout: config.Timeout,
		}
	}

	// Create transport
	tr := New(httpClient, config)

	return &Client{
		config:    config,
		transport: tr,
	}, nil
}

// ClientOption is a functional option for configuring the client
type ClientOption func(*Config)

// WithBaseURL sets a custom base URL
func WithBaseURL(baseURL string) ClientOption {
	return func(c *Config) {
		c.BaseURL = baseURL
	}
}

// WithTimeout sets a custom timeout
func WithTimeout(timeout time.Duration) ClientOption {
	return func(c *Config) {
		c.Timeout = timeout
	}
}

// WithMaxRetries sets the maximum number of retries
func WithMaxRetries(maxRetries int) ClientOption {
	return func(c *Config) {
		c.MaxRetries = maxRetries
	}
}

// WithHTTPClient sets a custom HTTP client
func WithHTTPClient(httpClient *http.Client) ClientOption {
	return func(c *Config) {
		c.HTTPClient = httpClient
	}
}

// WithPollingPeriod sets the polling period for async jobs
func WithPollingPeriod(period time.Duration) ClientOption {
	return func(c *Config) {
		c.PollingPeriod = period
	}
}

// WithHeader adds a custom header
func WithHeader(key, value string) ClientOption {
	return func(c *Config) {
		c.Headers[key] = value
	}
}

// GetConfig returns the client configuration
func (c *Client) GetConfig() *Config {
	return c.config
}

// Close closes the client and cleans up resources
func (c *Client) Close() error {
	// Transport cleanup is handled by the HTTP client
	return nil
}
