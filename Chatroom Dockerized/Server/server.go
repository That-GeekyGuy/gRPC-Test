package main

import (
	"io"
	"log"
	"net"
	"sync"

	pb "server/chat"

	"google.golang.org/grpc"
)

type clientStream struct {
	username string
	stream   pb.ChatService_ChatStreamServer
}

type chatServer struct {
	pb.UnimplementedChatServiceServer
	mu      sync.Mutex
	clients map[string]clientStream // map from username to stream
}

func newChatServer() *chatServer {
	return &chatServer{
		clients: make(map[string]clientStream),
	}
}

func (s *chatServer) ChatStream(stream pb.ChatService_ChatStreamServer) error {
	var username string

	// First message must contain sender's name
	firstMsg, err := stream.Recv()
	if err != nil {
		log.Printf("Failed to receive initial message: %v", err)
		return err
	}

	username = firstMsg.Sender
	log.Printf("%s joined the chat", username)

	s.mu.Lock()
	s.clients[username] = clientStream{username, stream}
	s.mu.Unlock()

	// Notify others about new user
	s.broadcast(pb.ChatMessage{
		Sender:  "Server",
		Message: username + " joined the chat",
	})

	// Handle continuous messages
	for {
		msg, err := stream.Recv()
		if err == io.EOF {
			log.Printf("%s left the chat", username)
			break
		}
		if err != nil {
			log.Printf("Receive error from %s: %v", username, err)
			break
		}

		log.Printf("[%s]: %s", msg.Sender, msg.Message)
		s.broadcast(*msg)
	}

	// Remove client on disconnect
	s.mu.Lock()
	delete(s.clients, username)
	s.mu.Unlock()

	// Notify others
	s.broadcast(pb.ChatMessage{
		Sender:  "Server",
		Message: username + " left the chat",
	})

	return nil
}

func (s *chatServer) broadcast(msg pb.ChatMessage) {
	s.mu.Lock()
	defer s.mu.Unlock()

	for name, client := range s.clients {
		if err := client.stream.Send(&msg); err != nil {
			log.Printf("Send error to %s: %v", name, err)
		}
	}
}

func main() {
	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	s := grpc.NewServer()
	pb.RegisterChatServiceServer(s, newChatServer())

	log.Println("Chatroom server started on :50051")
	if err := s.Serve(lis); err != nil {
		log.Fatalf("Server error: %v", err)
	}
}
