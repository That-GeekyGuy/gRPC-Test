import grpc
import serv_pb2
import serv_pb2_grpc

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = serv_pb2_grpc.GreeterStub(channel)
    response = stub.SayHello(serv_pb2.HelloRequest(name='Ansh'))
    print("Client received:", response.message)

if __name__ == '__main__':
    run()
