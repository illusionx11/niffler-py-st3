import grpc
import allure
from typing import Callable
from google.protobuf.message import Message
from google.protobuf.json_format import MessageToJson


class AllureInterceptor(grpc.UnaryUnaryClientInterceptor):
    
    def intercept_unary_unary(
        self, continuation: Callable, 
        client_call_details: grpc.ClientCallDetails, request: Message
    ) -> Callable:
        with allure.step(client_call_details.method):
            allure.attach(
                body=MessageToJson(request),
                name="Request",
                attachment_type=allure.attachment_type.JSON
            )
            response = continuation(client_call_details, request)
            allure.attach(
                body=MessageToJson(response.result()),
                name="Response",
                attachment_type=allure.attachment_type.JSON
            )
            return response