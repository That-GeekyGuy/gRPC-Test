import grpc
from concurrent import futures
import weather_pb2
import weather_pb2_grpc
import os
import time
from datetime import datetime
import requests

API_KEY = "6b295886c3ee4b1bab592705250407"
BASE_URL = "http://api.weatherapi.com/v1/current.json"

class WeatherService(weather_pb2_grpc.WeatherServiceServicer):
    def StreamWeather(self, request, context):
        city = request.city

        for _ in range(6):  # Stream every 10s for 1 minute
            params = {
                "key": API_KEY,
                "q": city,
                "aqi": "no"
            }

            try:
                res = requests.get(BASE_URL, params=params)
                data = res.json()

                if res.status_code != 200 or "error" in data:
                    msg = data.get("error", {}).get("message", "Invalid request")
                    context.set_details(msg)
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    return

                current = data["current"]
                location = data["location"]

                yield weather_pb2.WeatherResponse(
                    city=location["name"],
                    description=current["condition"]["text"],
                    temperature=current["temp_c"],
                    humidity=current["humidity"],
                    timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                )

            except Exception as e:
                context.set_details(str(e))
                context.set_code(grpc.StatusCode.INTERNAL)
                return

            time.sleep(10)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    weather_pb2_grpc.add_WeatherServiceServicer_to_server(WeatherService(), server)
    server.add_insecure_port('[::]:50051')
    print("🚀 gRPC Weather Server (WeatherAPI.com) running on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
