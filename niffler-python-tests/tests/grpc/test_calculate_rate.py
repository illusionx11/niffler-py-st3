import grpc
import pytest
import allure
from internal.pb.niffler_currency_pb2 import CurrencyValues
from internal.pb.niffler_currency_pb2_pbreflect import NifflerCurrencyServiceClient
from internal.pb.niffler_currency_pb2 import CalculateRequest
from utils.allure_data import Epic, Feature, Story

pytestmark = [pytest.mark.allure_label(label_type="epic", value=Epic.app_name)]

@pytest.mark.usefixtures("grpc_client", "mock")
@pytest.mark.grpc
@pytest.mark.currencies
@allure.feature(Feature.currencies)
@allure.story(Story.calculate_rate)
class TestCalculateRate:
    
    def test_calculate_rate(self, grpc_client: NifflerCurrencyServiceClient):
        try:
            response = grpc_client.calculate_rate(
                request=CalculateRequest(
                    spendCurrency=CurrencyValues.EUR,
                    desiredCurrency=CurrencyValues.RUB,
                    amount=100.0
                )
            )
            # Логика для основного сервера
            with allure.step("Проверка расчета курса"):
                assert response.calculatedAmount == 7200
        except grpc.RpcError as e:
            # Логика для mock сервера
            with allure.step("Проверка ошибки mock-сервера"):
                assert e.code() == grpc.StatusCode.NOT_FOUND
                assert "Request was not matched" in e.details()

    @pytest.mark.parametrize(
        "spend_currency, desired_currency, amount, expected_amount", [
            (CurrencyValues.USD, CurrencyValues.RUB, 100.0, 6666.67),
            (CurrencyValues.RUB, CurrencyValues.USD, 100.0, 1.5),
            (CurrencyValues.USD, CurrencyValues.USD, 100.0, 100.0)
        ]
    )
    def test_currency_conversion(
        self,
        grpc_client: NifflerCurrencyServiceClient,
        spend_currency: CurrencyValues,
        desired_currency: CurrencyValues,
        amount: float,
        expected_amount: float
    ):
        response = grpc_client.calculate_rate(
            request=CalculateRequest(
                spendCurrency=spend_currency,
                desiredCurrency=desired_currency,
                amount=amount
            )
        )
        with allure.step("Проверка расчета курса"):
            assert response.calculatedAmount == expected_amount

    @pytest.mark.parametrize("spend_currency, amount", [
        (CurrencyValues.EUR, 100.0),
        (CurrencyValues.RUB, 200.0),
        (CurrencyValues.USD, 345.0)
    ])
    def test_calculate_rate__without_desired_currency(
        self,
        grpc_client: NifflerCurrencyServiceClient,
        spend_currency: CurrencyValues, 
        amount: float, 
        mock: bool
    ):
        try:
            grpc_client.calculate_rate(
                request=CalculateRequest(
                    spendCurrency=spend_currency,
                    amount=amount
                )
            )
        except grpc.RpcError as e:
            if mock:
                with allure.step("Проверка ошибки mock-сервера"):
                    assert e.code() == grpc.StatusCode.NOT_FOUND
                    assert "Request was not matched" in e.details()
            else:
                with allure.step("Проверка ошибки основного сервера"):
                    assert e.code() == grpc.StatusCode.UNKNOWN
                    assert e.details() == "Application error processing RPC"

    @pytest.mark.parametrize("desired_currency, amount", [
        (CurrencyValues.EUR, 100.0),
        (CurrencyValues.RUB, 200.0),
        (CurrencyValues.USD, 345.0)
    ])
    def test_calculate_rate__without_spend_currency(
        self,
        grpc_client: NifflerCurrencyServiceClient,
        desired_currency: CurrencyValues, 
        amount: float, 
        mock: bool
    ):
        try:
            grpc_client.calculate_rate(
                request=CalculateRequest(
                    desiredCurrency=desired_currency,
                    amount=amount
                )
            )
        except grpc.RpcError as e:
            if mock:
                with allure.step("Проверка ошибки mock-сервера"):
                    assert e.code() == grpc.StatusCode.NOT_FOUND
                    assert "Request was not matched" in e.details()
            else:
                with allure.step("Проверка ошибки основного сервера"):
                    assert e.code() == grpc.StatusCode.UNKNOWN
                    assert e.details() == "Application error processing RPC"
                
    @pytest.mark.parametrize("spend_currency, desired_currency", [
        (CurrencyValues.EUR, CurrencyValues.RUB),
        (CurrencyValues.RUB, CurrencyValues.USD),
        (CurrencyValues.USD, CurrencyValues.EUR)
    ])
    def test_calculate_rate__without_amount(
        self,
        grpc_client: NifflerCurrencyServiceClient,
        spend_currency: CurrencyValues, 
        desired_currency: CurrencyValues,
        mock: bool
    ):
        try:
            grpc_client.calculate_rate(
                request=CalculateRequest(
                    spendCurrency=spend_currency,
                    desiredCurrency=desired_currency
                )
            )
        except grpc.RpcError as e:
            if mock:
                with allure.step("Проверка ошибки mock-сервера"):
                    assert e.code() == grpc.StatusCode.NOT_FOUND
                    assert "Request was not matched" in e.details()
            else:
                with allure.step("Проверка ошибки основного сервера"):
                    assert e.code() == grpc.StatusCode.UNKNOWN
                    assert e.details() == "Application error processing RPC"
                
    @pytest.mark.parametrize("spend_currency, desired_currency", [
        (CurrencyValues.EUR, CurrencyValues.RUB),
        (CurrencyValues.RUB, CurrencyValues.USD),
        (CurrencyValues.USD, CurrencyValues.EUR)
    ])
    def test_calculate_rate__with_zero_amount(
        self,
        grpc_client: NifflerCurrencyServiceClient,
        spend_currency: CurrencyValues, 
        desired_currency: CurrencyValues
    ):
        try:
            response = grpc_client.calculate_rate(
                request=CalculateRequest(
                    spendCurrency=spend_currency,
                    desiredCurrency=desired_currency,
                    amount=0.0
                )
            )
            # Логика для основного сервера
            with allure.step("Проверка расчета курса"):
                assert response.calculatedAmount == 0.0
        except grpc.RpcError as e:
            # Логика для mock сервера
            with allure.step("Проверка ошибки mock-сервера"):
                assert e.code() == grpc.StatusCode.NOT_FOUND
                assert "Request was not matched" in e.details()
            
    @pytest.mark.parametrize("amount", [-100.0, -200.0, -345.0])
    def test_calculate_rate__with_negative_amount(
        self,
        grpc_client: NifflerCurrencyServiceClient,
        amount: float,
        mock: bool
    ):
        try:
            response = grpc_client.calculate_rate(
                request=CalculateRequest(
                    spendCurrency=CurrencyValues.EUR,
                    desiredCurrency=CurrencyValues.RUB,
                    amount=amount
                )
            )
            # Логика для основного сервера
            with allure.step("Проверка расчета курса"):
                assert response.calculatedAmount == 0.0
        except AssertionError:
            if not mock:
                pytest.xfail(reason="Негативные значения должны возвращать 0.0")
            raise
        except grpc.RpcError as e:
            # Логика для mock сервера
            if mock:
                with allure.step("Проверка ошибки mock-сервера"):
                    assert e.code() == grpc.StatusCode.NOT_FOUND
                    assert "Request was not matched" in e.details()
            else:
                pytest.fail(f"Ошибка: {e.details()}\nКод ошибки: {e.code()}")