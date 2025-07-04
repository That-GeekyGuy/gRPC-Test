import grpc
import chat_pb2
import chat_pb2_grpc

def request_messages(sender):
    try:
        while True:
            msg = input("You: ")
            if not msg:
                break
            yield chat_pb2.ChatMessage(sender=sender, message=msg)
    except KeyboardInterrupt:
        print("Exiting send thread")
        return

def receive_messages(response_stream):
    try:
        for response in response_stream:
            print(f"{response.sender}: {response.message}")
    except grpc.RpcError as e:
        print("Stream closed.")

def run():
    sender = input("Enter your name: ")
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = chat_pb2_grpc.ChatServiceStub(channel)
        response_stream = stub.ChatStream(request_messages(sender))
        receive_messages(response_stream)

if __name__ == "__main__":
    run()
