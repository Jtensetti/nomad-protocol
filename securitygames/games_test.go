package securitygames

import "testing"

func TestReaderWorldIdentical(t *testing.T) {
	a := ReaderWorld(16, 1200, 15)
	b := ReaderWorld(16, 1200, 15)
	if a != b {
		t.Fatal("ideal reader worlds differ")
	}
}

func TestShuffleBaseline(t *testing.T) {
	got, err := ShuffleGuessRecall(2000, 16, 2000)
	if err != nil {
		t.Fatal(err)
	}
	want := 16.0 / 2000.0
	if got < want*0.5 || got > want*1.5 {
		t.Fatalf("got %.5f want near %.5f", got, want)
	}
}
