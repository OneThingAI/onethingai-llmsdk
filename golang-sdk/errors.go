package onethingai

import (
	"errors"
	"fmt"
)

// Common errors
var (
	// ErrInvalidAPIKey is returned when the API key is invalid or missing
	ErrInvalidAPIKey = errors.New("invalid or missing API key")

	// ErrInvalidRequest is returned when the request is malformed
	ErrInvalidRequest = errors.New("invalid request")

	// ErrRateLimitExceeded is returned when rate limit is exceeded
	ErrRateLimitExceeded = errors.New("rate limit exceeded")

	// ErrServerError is returned when the server encounters an error
	ErrServerError = errors.New("server error")

	// ErrJobNotFound is returned when a job is not found
	ErrJobNotFound = errors.New("job not found")

	// ErrJobFailed is returned when a job fails
	ErrJobFailed = errors.New("job failed")

	// ErrTimeout is returned when a request times out
	ErrTimeout = errors.New("request timeout")

	// ErrCancelled is returned when a request is cancelled
	ErrCancelled = errors.New("request cancelled")
)

// HTTPError represents an API error response
type HTTPError struct {
	StatusCode int
	Message    string
	Body       string
}

func (e *HTTPError) Error() string {
	return fmt.Sprintf("HTTP %d: %s", e.StatusCode, e.Message)
}

// ValidationError represents a validation error
type ValidationError struct {
	Field   string
	Message string
}

func (e *ValidationError) Error() string {
	return fmt.Sprintf("validation error on field '%s': %s", e.Field, e.Message)
}

// NewValidationError creates a new validation error
func NewValidationError(field, message string) error {
	return &ValidationError{
		Field:   field,
		Message: message,
	}
}

// IsHTTPError checks if an error is an HTTP error
func IsHTTPError(err error) bool {
	_, ok := err.(*HTTPError)
	return ok
}

// IsValidationError checks if an error is a validation error
func IsValidationError(err error) bool {
	_, ok := err.(*ValidationError)
	return ok
}

// GetHTTPStatusCode returns the HTTP status code from an error, or 0 if not an HTTP error
func GetHTTPStatusCode(err error) int {
	if httpErr, ok := err.(*HTTPError); ok {
		return httpErr.StatusCode
	}
	return 0
}

// IsRateLimitError checks if an error is a rate limit error
func IsRateLimitError(err error) bool {
	if httpErr, ok := err.(*HTTPError); ok {
		return httpErr.StatusCode == 429
	}
	return errors.Is(err, ErrRateLimitExceeded)
}

// IsAuthError checks if an error is an authentication error
func IsAuthError(err error) bool {
	if httpErr, ok := err.(*HTTPError); ok {
		return httpErr.StatusCode == 401 || httpErr.StatusCode == 403
	}
	return errors.Is(err, ErrInvalidAPIKey)
}

// IsServerError checks if an error is a server error
func IsServerError(err error) bool {
	if httpErr, ok := err.(*HTTPError); ok {
		return httpErr.StatusCode >= 500
	}
	return errors.Is(err, ErrServerError)
}

// WrapError wraps an error with additional context
func WrapError(err error, message string) error {
	if err == nil {
		return nil
	}
	return fmt.Errorf("%s: %w", message, err)
}
