package onethingai

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
)

// StreamReader reads SSE (Server-Sent Events) streams
type StreamReader[T any] struct {
	resp   *http.Response
	reader *bufio.Reader
	ctx    context.Context
}

// NewStreamReader creates a new stream reader
func NewStreamReader[T any](ctx context.Context, resp *http.Response) *StreamReader[T] {
	return &StreamReader[T]{
		resp:   resp,
		reader: bufio.NewReader(resp.Body),
		ctx:    ctx,
	}
}

// Next reads the next event from the stream
func (s *StreamReader[T]) Next() (*StreamDataResponse[T], error) {
	// Check if context is cancelled
	select {
	case <-s.ctx.Done():
		return nil, s.ctx.Err()
	default:
	}

	for {
		line, err := s.reader.ReadString('\n')
		if err != nil {
			if err == io.EOF {
				return nil, io.EOF
			}
			return nil, fmt.Errorf("failed to read stream: %w", err)
		}

		line = strings.TrimSpace(line)

		// Skip empty lines and comments
		if line == "" || strings.HasPrefix(line, ":") {
			continue
		}

		// Parse SSE format: "data: {...}"
		if strings.HasPrefix(line, "data: ") {
			data := strings.TrimPrefix(line, "data: ")

			// Handle [DONE] signal
			if data == "[DONE]" {
				return nil, io.EOF
			}

			// Parse JSON data
			var event StreamDataResponse[T]
			if err := json.Unmarshal([]byte(data), &event); err != nil {
				return nil, fmt.Errorf("failed to parse stream event: %w", err)
			}

			return &event, nil
		}
	}
}

// Close closes the stream
func (s *StreamReader[T]) Close() error {
	if s.resp != nil && s.resp.Body != nil {
		return s.resp.Body.Close()
	}
	return nil
}

// ReadAll reads all events from the stream until done
func (s *StreamReader[T]) ReadAll() ([]StreamDataResponse[T], error) {
	var events []StreamDataResponse[T]

	for {
		event, err := s.Next()
		if err != nil {
			if err == io.EOF {
				break
			}
			return events, err
		}

		events = append(events, *event)

		// Stop if we receive a done event
		if event.IsDone() {
			break
		}
	}

	return events, nil
}

// TextStreamReader reads text streaming responses (e.g., OpenAI-style streaming)
type TextStreamReader struct {
	resp   *http.Response
	reader *bufio.Reader
	ctx    context.Context
}

// NewTextStreamReader creates a new text stream reader
func NewTextStreamReader(ctx context.Context, resp *http.Response) *TextStreamReader {
	return &TextStreamReader{
		resp:   resp,
		reader: bufio.NewReader(resp.Body),
		ctx:    ctx,
	}
}

// Next reads the next chunk from the text stream
func (s *TextStreamReader) Next() (map[string]interface{}, error) {
	// Check if context is cancelled
	select {
	case <-s.ctx.Done():
		return nil, s.ctx.Err()
	default:
	}

	var dataBuffer bytes.Buffer

	for {
		line, err := s.reader.ReadString('\n')
		if err != nil {
			if err == io.EOF {
				return nil, io.EOF
			}
			return nil, fmt.Errorf("failed to read stream: %w", err)
		}

		line = strings.TrimSpace(line)

		// Skip empty lines
		if line == "" {
			if dataBuffer.Len() > 0 {
				// Parse accumulated data
				var result map[string]interface{}
				if err := json.Unmarshal(dataBuffer.Bytes(), &result); err != nil {
					return nil, fmt.Errorf("failed to parse stream data: %w", err)
				}
				return result, nil
			}
			continue
		}

		// Parse SSE format
		if strings.HasPrefix(line, "data: ") {
			data := strings.TrimPrefix(line, "data: ")

			// Handle [DONE] signal
			if data == "[DONE]" {
				return nil, io.EOF
			}

			dataBuffer.WriteString(data)
		} else if strings.HasPrefix(line, ":") {
			// Skip comments
			continue
		}
	}
}

// Close closes the stream
func (s *TextStreamReader) Close() error {
	if s.resp != nil && s.resp.Body != nil {
		return s.resp.Body.Close()
	}
	return nil
}

// Stream helper function to process stream events with a callback
func Stream[T any](ctx context.Context, reader *StreamReader[T], callback func(*StreamDataResponse[T]) error) error {
	defer reader.Close()

	for {
		event, err := reader.Next()
		if err != nil {
			if err == io.EOF {
				return nil
			}
			return err
		}

		if err := callback(event); err != nil {
			return err
		}

		// Stop processing if we receive a done event
		if event.IsDone() {
			break
		}

		// Stop processing if we receive an error event
		if event.IsError() {
			return fmt.Errorf("stream error: %v", event.Error)
		}
	}

	return nil
}
