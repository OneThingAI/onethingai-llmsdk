package onethingai

import (
	"context"
	"net/http"
)

// doRequest performs an HTTP request with retry logic
func (c *Client) doRequest(ctx context.Context, method, path string, body interface{}, result interface{}) error {
	return c.transport.DoRequest(ctx, method, path, body, result)
}

// doStreamRequest performs a streaming HTTP request
func (c *Client) doStreamRequest(ctx context.Context, method, path string, body interface{}) (*http.Response, error) {
	return c.transport.DoStreamRequest(ctx, method, path, body)
}
