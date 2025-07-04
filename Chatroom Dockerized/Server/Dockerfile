# Use updated Go version that meets go.mod requirement
FROM golang:1.24.4

WORKDIR /app

# Copy project files into container
COPY . .

# Download Go dependencies
RUN go mod download

# Build the Go server
RUN go build -o chatserver server.go

# Expose gRPC port
EXPOSE 50051

# Run the server
CMD ["./chatserver"]
