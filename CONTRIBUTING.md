# Contributing

Security claims require tests. A change that affects traffic scheduling, mixing, semantic metadata or reconstruction must include an adversarial test describing what an observer learns before and after the change.

Use `gofmt`, `go test -race ./...` and `go vet ./...` before submitting changes.
