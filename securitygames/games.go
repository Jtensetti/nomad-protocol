package securitygames

import (
	"crypto/rand"
	"encoding/binary"
	"errors"
	"math"
)

type Trace struct {
	Cells     int
	Bytes     int
	PeerSlots uint64
}

// ReaderWorld returns the externally visible trace for a local reader action.
// By construction, activity is not an input. This encodes the ideal Selection
// Firewall security game, not a claim about an unreviewed real deployment.
func ReaderWorld(cells, cellSize int, peerMask uint64) Trace {
	return Trace{Cells: cells, Bytes: cells * cellSize, PeerSlots: peerMask}
}

func ReaderAdvantage(samples int) (float64, error) {
	if samples <= 0 {
		return 0, errors.New("samples must be positive")
	}
	correct := 0
	for i := 0; i < samples; i++ {
		bit, err := randomBit()
		if err != nil {
			return 0, err
		}
		_ = ReaderWorld(16, 1200, 0x0f) // identical in both worlds
		guess, err := randomBit()
		if err != nil {
			return 0, err
		}
		if bit == guess {
			correct++
		}
	}
	accuracy := float64(correct) / float64(samples)
	return math.Abs(accuracy - 0.5), nil
}

func randomBit() (int, error) {
	var b [1]byte
	if _, err := rand.Read(b[:]); err != nil {
		return 0, err
	}
	return int(b[0] & 1), nil
}

// ShuffleGuessRecall estimates the probability of linking a target output after
// a perfect secret permutation when the adversary has no distinguishing signal.
func ShuffleGuessRecall(batch, target, rounds int) (float64, error) {
	if batch <= 0 || target <= 0 || target > batch || rounds <= 0 {
		return 0, errors.New("invalid parameters")
	}
	hits := 0
	for r := 0; r < rounds; r++ {
		truth, err := sampleDistinct(batch, target)
		if err != nil {
			return 0, err
		}
		guess, err := sampleDistinct(batch, target)
		if err != nil {
			return 0, err
		}
		set := make(map[int]struct{}, target)
		for _, x := range truth {
			set[x] = struct{}{}
		}
		for _, x := range guess {
			if _, ok := set[x]; ok {
				hits++
			}
		}
	}
	return float64(hits) / float64(rounds*target), nil
}

func sampleDistinct(n, k int) ([]int, error) {
	a := make([]int, n)
	for i := range a {
		a[i] = i
	}
	for i := 0; i < k; i++ {
		jn, err := uniform(n - i)
		if err != nil {
			return nil, err
		}
		j := i + jn
		a[i], a[j] = a[j], a[i]
	}
	return a[:k], nil
}
func uniform(n int) (int, error) {
	limit := ^uint64(0) - (^uint64(0) % uint64(n))
	for {
		var b [8]byte
		if _, err := rand.Read(b[:]); err != nil {
			return 0, err
		}
		v := binary.BigEndian.Uint64(b[:])
		if v < limit {
			return int(v % uint64(n)), nil
		}
	}
}
