import grpc
from typing import Callable
from google.protobuf.message import Message


class LoggingInterceptor(grpc.UnaryUnaryClientInterceptor):
    
    def intercept_unary_unary(
        self, continuation: Callable, 
        client_call_details: grpc.ClientCallDetails, request: Message
    ) -> Callable:
        print(f"Method: {client_call_details.method}")
        print(f"Request: {request}")
        response = continuation(client_call_details, request)
        print(f"Response: {response.result()}")
        return response