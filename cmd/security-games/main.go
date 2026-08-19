package main

import (
	"fmt"
	"github.com/Jtensetti/nomad-protocol/securitygames"
)

func main() {
	adv, err := securitygames.ReaderAdvantage(500000)
	if err != nil {
		panic(err)
	}
	recall, err := securitygames.ShuffleGuessRecall(5000, 16, 10000)
	if err != nil {
		panic(err)
	}
	fmt.Printf("ideal reader distinguishing advantage: %.6f\n", adv)
	fmt.Printf("shuffle target recall: %.6f (random baseline %.6f)\n", recall, 16.0/5000.0)
}
