package onethingai

import (
	"context"
	"fmt"
)

// validateVideoRequest validates and prepares video request
func validateVideoRequest(req interface{}, syncMode SyncMode) error {
	switch r := req.(type) {
	case *VideoRequest:
		if r.Model == "" {
			return fmt.Errorf("model is required")
		}
		if r.Prompt == "" {
			return fmt.Errorf("prompt is required")
		}
		if r.SyncMode == "" {
			r.SyncMode = syncMode
		}
		if r.JobType == "" {
			r.JobType = VideoJobTypeText2Video
		}
		r.Stream = nil
		return nil

	case map[string]interface{}:
		if model, ok := r["model"]; !ok || model == "" {
			return fmt.Errorf("model is required")
		}
		if prompt, ok := r["prompt"]; !ok || prompt == "" {
			return fmt.Errorf("prompt is required")
		}
		if _, ok := r["sync_mode"]; !ok {
			r["sync_mode"] = syncMode
		}
		if _, ok := r["job_type"]; !ok {
			r["job_type"] = VideoJobTypeText2Video
		}
		delete(r, "stream")
		return nil

	default:
		return fmt.Errorf("request must be *VideoRequest or map[string]interface{}")
	}
}

// GenerateVideo generates a video (non-streaming, async by default)
func (c *Client) GenerateVideo(ctx context.Context, req interface{}) (*VideoResponse, error) {
	if req == nil {
		return nil, fmt.Errorf("request cannot be nil")
	}

	if err := validateVideoRequest(req, SyncModeAsync); err != nil {
		return nil, err
	}

	var reqMap map[string]interface{}
	err := c.doRequest(ctx, "POST", "/generation", req, &reqMap)
	if err != nil {
		return nil, err
	}
	return NewVideoResponse(reqMap)
}

// WaitForVideo polls async video job until completion
func (c *Client) WaitForVideo(ctx context.Context, jobID string, opts *PollingOptions) (*VideoResponse, error) {
	return c.PollVideoJobStatus(ctx, jobID, opts)
}
