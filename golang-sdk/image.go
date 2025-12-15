package onethingai

import (
	"context"
	"fmt"
)

// validateImageRequest validates and prepares image request
func validateImageRequest(req interface{}, syncMode SyncMode, stream *bool) error {
	switch r := req.(type) {
	case *ImageRequest:
		if r.Model == "" {
			return fmt.Errorf("model is required")
		}
		if r.Prompt == "" {
			return fmt.Errorf("prompt is required")
		}
		r.SyncMode = syncMode
		if r.JobType == "" {
			r.JobType = ImageJobTypeGeneration
		}
		r.Stream = stream
		return nil

	case map[string]interface{}:
		if model, ok := r["model"]; !ok || model == "" {
			return fmt.Errorf("model is required")
		}
		if prompt, ok := r["prompt"]; !ok || prompt == "" {
			return fmt.Errorf("prompt is required")
		}
		r["sync_mode"] = syncMode
		if _, ok := r["job_type"]; !ok {
			r["job_type"] = ImageJobTypeGeneration
		}
		if stream != nil {
			r["stream"] = *stream
		} else {
			delete(r, "stream")
		}
		return nil

	default:
		return fmt.Errorf("request must be *ImageRequest or map[string]interface{}")
	}
}

// GenerateImage generates an image (non-streaming)
func (c *Client) GenerateImage(ctx context.Context, req interface{}) (*ImageResponse, error) {
	if req == nil {
		return nil, fmt.Errorf("request cannot be nil")
	}

	if err := validateImageRequest(req, SyncModeSync, nil); err != nil {
		return nil, err
	}

	var reqMap map[string]interface{}
	err := c.doRequest(ctx, "POST", "/generation", req, &reqMap)
	if err != nil {
		return nil, err
	}
	return NewImageResponse(reqMap)
}

// GenerateImageStream generates an image with streaming
func (c *Client) GenerateImageStream(ctx context.Context, req interface{}) (*StreamReader[ImageResult], error) {
	if req == nil {
		return nil, fmt.Errorf("request cannot be nil")
	}

	stream := true
	if err := validateImageRequest(req, SyncModeSync, &stream); err != nil {
		return nil, err
	}

	resp, err := c.doStreamRequest(ctx, "POST", "/generation", req)
	if err != nil {
		return nil, err
	}
	return NewStreamReader[ImageResult](ctx, resp), nil
}

// WaitForImage polls async job until completion
func (c *Client) WaitForImage(ctx context.Context, jobID string, opts *PollingOptions) (*ImageResponse, error) {
	return c.PollImageJobStatus(ctx, jobID, opts)
}
