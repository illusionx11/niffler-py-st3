import grpc
from typing import Callable
from google.protobuf.message import Message
import logging

class LoggingInterceptor(grpc.UnaryUnaryClientInterceptor):
    
    def intercept_unary_unary(
        self, continuation: Callable, 
        client_call_details: grpc.ClientCallDetails, request: Message
    ) -> Callable:
        logging.info(f"Method: {client_call_details.method}")
        logging.info(f"Request: {request}")
        response = continuation(client_call_details, request)
        logging.info(f"Response: {response.result()}")
        return response