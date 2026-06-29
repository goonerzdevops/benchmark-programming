package main

import (
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"log"
	"math"
	"net/http"
	"sort"
	"time"
)

type Item struct {
	NumericValue float64 `json:"numeric_value"`
	StringData   string  `json:"string_data"`
}

type InputData struct {
	Items []Item `json:"items"`
}

type TransformedItem struct {
	OriginalNumeric float64 `json:"original_numeric"`
	OriginalString  string  `json:"original_string"`
	NewValue        float64 `json:"new_value"`
}

type OutputData struct {
	AverageNumericValue      float64           `json:"average_numeric_value"`
	HashedCombinedString     string            `json:"hashed_combined_string"`
	TransformedSortedItems   []TransformedItem `json:"transformed_and_sorted_items"`
	ServerProcessingTimeMs   float64           `json:"server_processing_time_ms"`
}

func transformHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var data InputData
	if err := json.NewDecoder(r.Body).Decode(&data); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	start := time.Now()

	if len(data.Items) == 0 {
		http.Error(w, "Empty items array", http.StatusBadRequest)
		return
	}

	// Calculate average and combine strings
	var sumNumeric float64
	var combinedString string
	for _, item := range data.Items {
		sumNumeric += item.NumericValue
		combinedString += item.StringData
	}

	avgNumeric := sumNumeric / float64(len(data.Items))

	// SHA256 hash
	hash := sha256.Sum256([]byte(combinedString))
	hashedStr := fmt.Sprintf("%x", hash)

	// Transform
	combinedLen := float64(len(combinedString))
	transformed := make([]TransformedItem, len(data.Items))
	for i, item := range data.Items {
		newVal := (item.NumericValue * 1.5) + (combinedLen / 2.0)
		transformed[i] = TransformedItem{
			OriginalNumeric: item.NumericValue,
			OriginalString:  item.StringData,
			NewValue:        math.Round(newVal*100) / 100,
		}
	}

	// Sort by new value ascending
	sort.Slice(transformed, func(i, j int) bool {
		return transformed[i].NewValue < transformed[j].NewValue
	})

	elapsed := time.Since(start).Seconds() * 1000

	output := OutputData{
		AverageNumericValue:    math.Round(avgNumeric*100) / 100,
		HashedCombinedString:   hashedStr,
		TransformedSortedItems: transformed,
		ServerProcessingTimeMs: math.Round(elapsed*100) / 100,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(output)
}

func main() {
	http.HandleFunc("/complex-transform", transformHandler)
	log.Println("Go (net/http) server starting on :8893")
	log.Fatal(http.ListenAndServe(":8893", nil))
}
