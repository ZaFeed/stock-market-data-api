package main

import (
	"context"
	"encoding/json"
	"errors"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"
	"time"
)

type snapshotPage struct {
	Data []json.RawMessage `json:"data"`
	Meta *struct {
		Next string `json:"next"`
	} `json:"meta"`
}

func collect(ctx context.Context, client *http.Client, origin *url.URL, key string) ([]json.RawMessage, error) {
	const maxPages = 10
	rows := []json.RawMessage{}
	seen := map[string]bool{}
	cursor := ""
	for range maxPages {
		params := url.Values{"market": {"HK"}, "venue": {"HKEX"}, "limit": {"100"}}
		if cursor != "" {
			params.Set("cursor", cursor)
		}
		endpoint := origin.ResolveReference(&url.URL{Path: "/v1/snapshot", RawQuery: params.Encode()})
		request, err := http.NewRequestWithContext(ctx, http.MethodGet, endpoint.String(), nil)
		if err != nil {
			return nil, err
		}
		request.Header.Set("X-API-Key", key)
		reply, err := client.Do(request)
		if err != nil {
			return nil, err
		}
		var page snapshotPage
		if reply.StatusCode == http.StatusOK {
			err = json.NewDecoder(io.LimitReader(reply.Body, 2<<20)).Decode(&page)
		}
		reply.Body.Close()
		if reply.StatusCode != http.StatusOK || err != nil || page.Data == nil || page.Meta == nil {
			return nil, errors.New("invalid snapshot page")
		}
		rows = append(rows, page.Data...)
		cursor = page.Meta.Next
		if cursor == "" {
			return rows, nil
		}
		if seen[cursor] {
			return nil, errors.New("repeated snapshot cursor")
		}
		seen[cursor] = true
	}
	return nil, errors.New("snapshot exceeded page budget")
}

func main() {
	origin, err := url.Parse(os.Getenv("ZAFEED_BASE_URL"))
	key := os.Getenv("ZAFEED_HK_KEY")
	if err != nil || origin.Hostname() == "" || origin.User != nil || origin.RawQuery != "" || origin.Fragment != "" ||
		(origin.Path != "" && origin.Path != "/") || key == "" ||
		(origin.Scheme != "https" && !(origin.Scheme == "http" && origin.Hostname() == "127.0.0.1")) {
		log.Fatal("set ZAFEED_BASE_URL and ZAFEED_HK_KEY")
	}
	client := &http.Client{
		Timeout:       5 * time.Second,
		CheckRedirect: func(*http.Request, []*http.Request) error { return http.ErrUseLastResponse },
	}
	mux := http.NewServeMux()
	mux.HandleFunc("GET /hkex/snapshot", func(w http.ResponseWriter, r *http.Request) {
		ctx, cancel := context.WithTimeout(r.Context(), 12*time.Second)
		defer cancel()
		rows, err := collect(ctx, client, origin, key)
		if err != nil {
			http.Error(w, "Could not complete the snapshot", http.StatusBadGateway)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]any{"market": "HK", "venue": "HKEX", "data": rows})
	})
	port := os.Getenv("PORT")
	if port == "" {
		port = "8103"
	}
	server := &http.Server{Addr: "127.0.0.1:" + port, Handler: mux, ReadHeaderTimeout: 5 * time.Second}
	log.Fatal(server.ListenAndServe())
}
