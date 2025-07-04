FROM python:3.11-slim

WORKDIR /app

COPY client.py .
COPY chat_pb2.py .
COPY chat_pb2_grpc.py .

RUN pip install grpcio grpcio-tools

CMD ["python", "client.py"]
