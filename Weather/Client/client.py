import grpc
import weather_pb2
import weather_pb2_grpc

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = weather_pb2_grpc.WeatherServiceStub(channel)

    city = input("Enter city for weather updates: ")
    request = weather_pb2.WeatherRequest(city=city)

    try:
        for response in stub.StreamWeather(request):
            print(f"\n[{response.timestamp}] Weather in {response.city}:")
            print(f"  Description: {response.description}")
            print(f"  Temperature: {response.temperature}°C")
            print(f"  Humidity: {response.humidity}%")
    except grpc.RpcError as e:
        print(f"❌ gRPC Error: {e.details()}")
    except KeyboardInterrupt:
        print("\n⛔ Interrupted by user. Closing stream...")
    finally:
        channel.close()

if __name__ == '__main__':
    run()
