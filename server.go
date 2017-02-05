package main

import (
	"fmt"
	"net/http"
	"runtime"
	"strconv"
)

var (
	resp = map[int][]byte{
		1:   make([]byte, 1024),
		10:  make([]byte, 1024*10),
		100: make([]byte, 1024*100),
	}
)

func handler(w http.ResponseWriter, r *http.Request) {
	var size int

	rawSize := r.URL.Path[1:]
	size, err := strconv.Atoi(rawSize)
	if err != nil {
		size = 1
	}

	val, _ := resp[size]
	w.Write(val)
}

func main() {
	runtime.GOMAXPROCS(1)

	http.HandleFunc("/", handler)
	fmt.Println("Serving at http://127.0.0.1:8080 (go)")
	http.ListenAndServe("0.0.0.0:8080", nil)
}
