package onethingai

import (
	"context"
	"fmt"
	"time"
)

// PollingOptions configure async job polling behavior
type PollingOptions struct {
	// MaxAttempts is the maximum number of polling attempts (0 = unlimited)
	MaxAttempts int

	// Interval is the time between polling attempts
	Interval time.Duration

	// Timeout is the maximum time to wait for job completion
	Timeout time.Duration

	// OnProgress is called on each polling iteration with progress update
	OnProgress func(progress float64, status Status)
}

// DefaultPollingOptions returns default polling options
func DefaultPollingOptions() *PollingOptions {
	return &PollingOptions{
		MaxAttempts: 0, // unlimited
		Interval:    2 * time.Second,
		Timeout:     5 * time.Minute,
		OnProgress:  nil,
	}
}

// pollJobStatus is a generic internal polling function for image and video jobs
func pollJobStatus[T any](
	ctx context.Context,
	jobID string,
	opts *PollingOptions,
	getStatus func(context.Context, string) (*Response[ImageAndVideoDataResponse[T]], error),
) (*Response[ImageAndVideoDataResponse[T]], error) {
	if opts == nil {
		opts = DefaultPollingOptions()
	}

	// Create context with timeout if specified
	if opts.Timeout > 0 {
		var cancel context.CancelFunc
		ctx, cancel = context.WithTimeout(ctx, opts.Timeout)
		defer cancel()
	}

	attempt := 0
	ticker := time.NewTicker(opts.Interval)
	defer ticker.Stop()

	for {
		if opts.MaxAttempts > 0 && attempt >= opts.MaxAttempts {
			return nil, fmt.Errorf("max polling attempts (%d) exceeded", opts.MaxAttempts)
		}

		resp, err := getStatus(ctx, jobID)
		if err != nil {
			// 可选：log.Printf("polling attempt %d failed: %v", attempt+1, err)
			select {
			case <-ctx.Done():
				return nil, ctx.Err()
			case <-ticker.C:
				attempt++
				continue
			}
		}

		if opts.OnProgress != nil {
			opts.OnProgress(resp.Data.Progress, resp.Data.Status)
		}
		if resp.Data.IsCompleted() {
			return resp, nil
		}
		if resp.Data.IsFailed() {
			return resp, fmt.Errorf("job failed: %v", resp.Data.Error)
		}

		select {
		case <-ctx.Done():
			return nil, ctx.Err()
		case <-ticker.C:
			attempt++
		}
	}
}

// PollImageJobStatus polls a job until it's completed or failed
func (c *Client) PollImageJobStatus(ctx context.Context, jobID string, opts *PollingOptions) (*ImageResponse, error) {
	return pollJobStatus(ctx, jobID, opts, c.GetImageJobStatus)
}

// PollVideoJobStatus polls a video job until it's completed or failed
func (c *Client) PollVideoJobStatus(ctx context.Context, jobID string, opts *PollingOptions) (*VideoResponse, error) {
	return pollJobStatus(ctx, jobID, opts, c.GetVideoJobStatus)
}

// getJobStatus is a generic internal function to retrieve job status
func getJobStatus[T any](
	c *Client,
	ctx context.Context,
	jobID string,
	parseFunc func(interface{}) (*Response[T], error),
) (*Response[T], error) {
	var respMap map[string]interface{}
	path := fmt.Sprintf("/generation/job/%s", jobID)
	err := c.doRequest(ctx, "GET", path, nil, &respMap)
	if err != nil {
		return nil, err
	}
	return parseFunc(respMap)
}

// GetImageJobStatus retrieves the status of an image generation job
func (c *Client) GetImageJobStatus(ctx context.Context, jobID string) (*ImageResponse, error) {
	return getJobStatus(c, ctx, jobID, NewImageResponse)
}

// GetVideoJobStatus retrieves the status of a video generation job
func (c *Client) GetVideoJobStatus(ctx context.Context, jobID string) (*VideoResponse, error) {
	return getJobStatus(c, ctx, jobID, NewVideoResponse)
}
