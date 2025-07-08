package main

import (
	"fmt"
	"log"
	"net/http"
)

func handler(w http.ResponseWriter, r *http.Request) {
	fmt.Println("ping")
}

func main() {
	http.HandleFunc("/", handler)

	port := ":29785"
	fmt.Printf("Serveur démarré sur http://localhost%s\n", port)
	err := http.ListenAndServe(port, nil)
	if err != nil {
		log.Fatalf("Erreur lors du démarrage du serveur : %v", err)
	}
}
