from http import HTTPStatus
from fastapi.testclient import TestClient
from pydantic_core import ValidationError
import pytest
import datetime
from starlette.responses import JSONResponse
from .app import app, Deposit, check_correctness_of_date, deposit_algorithm

client = TestClient(app)


def test_deposit_model_with_periods_more_than_possible():
    """Expect test to raise error because periods is more than 60"""
    with pytest.raises(ValidationError):
        Deposit(date="17.01.2024", periods=1000, amount=10000, rate=3.2)


def test_deposit_model_with_periods_less_than_possible():
    """Expect test to raise error because periods is less than 1"""
    with pytest.raises(ValidationError):
        Deposit(date="18.01.2024", periods=0, amount=10000, rate=3.3)


def test_deposit_model_with_periods_non_integer():
    """Expect test to raise error because periods is not integer value"""
    with pytest.raises(ValidationError):
        Deposit(date="19.01.2024", periods="periods", amount=10000, rate=3.4)


def test_deposit_model_with_amount_more_than_possible():
    """Expect test to raise error because amount is more than 3000000"""
    with pytest.raises(ValidationError):
        Deposit(date="20.01.2024", periods=5, amount=1000000000, rate=3.5)


def test_deposit_model_with_amount_less_than_possible():
    """Expect test to raise error because amount is less than 10000"""
    with pytest.raises(ValidationError):
        Deposit(date="21.01.2024", periods=6, amount=5000, rate=3.6)


def test_deposit_model_with_amount_non_integer():
    """Expect test to raise error because amount is not integer value"""
    with pytest.raises(ValidationError):
        Deposit(date="22.01.2024", periods=7, amount=10000.02139, rate=3.7)


def test_deposit_model_with_rate_more_than_possible():
    """Expect test to raise error because rate is more than 8"""
    with pytest.raises(ValidationError):
        Deposit(date="23.01.2024", periods=9, amount=100000, rate=10.6)


def test_deposit_model_with_rate_less_than_possible():
    """Expect test to raise error because rate is less than 1"""
    with pytest.raises(ValidationError):
        Deposit(date="23.01.2024", periods=10, amount=1000000, rate=0.6)


def test_deposit_model_with_rate_non_float():
    """Expect test to raise error because rate is not float value"""
    with pytest.raises(ValidationError):
        Deposit(date="23.01.2024", periods=10, amount=1000000, rate="something wrong")


def test_deposit_model_without_rate():
    """Expect test to raise error because rate is not initialized"""
    with pytest.raises(ValidationError):
        Deposit(date="24.01.2024", periods=10, amount=1000000)


def test_deposit_model_without_periods():
    """Expect test to raise error because periods is not initialized"""
    with pytest.raises(ValidationError):
        Deposit(date="25.01.2024", amount=1000000, rate=4.2)


def test_deposit_model_without_amount():
    """Expect test to raise error because periods is not initialized"""
    with pytest.raises(ValidationError):
        Deposit(date="26.01.2024", periods=10, rate=4.4)


def test_deposit_model_without_date():
    """Expect test to raise error because date is not initialized"""
    with pytest.raises(ValidationError):
        Deposit(periods=10, amount=1000000, rate=4.7)


def test_deposit_model_with_date_in_wrong_format():
    r"""Expect test to raise error because date does not match pattern ^\d{2}\.\d{2}\.\d{4}$"""
    with pytest.raises(ValidationError):
        Deposit(date="27/01/2024", periods=33, amount=35000, rate=3.9)


def test_deposit_model_with_date_non_string():
    """Expect test to raise error because date is not string value"""
    with pytest.raises(ValidationError):
        Deposit(date=10000213193, periods=33, amount=35000, rate=3.9)


def test_handler_with_empty_body():
    """Request with empty body, should be bad request"""
    response = client.post("/calculate")
    assert response.status_code == 400
    assert response.json() == {"error": "Problem occurred with body. Missing body."}


def test_handler_with_only_one_of_required_fields():
    """Request with only one of four required fields, should be bad request"""
    response = client.post("/calculate", json={"periods": 30})
    assert response.status_code == 400
    assert response.json() == {"error": "Problem occurred with json field date: Field required. Problem occurred with "
                                        "json field amount: Field required. Problem occurred with json field rate: "
                                        "Field required"}


def test_handler_with_wrong_input_for_one_of_the_fields():
    """Request with wrong input for one of the required fields, should be bad request"""
    response = client.post("/calculate", json={"date": 2002, "periods": 10, "amount": 100000, "rate": 3.9})
    assert response.status_code == 400
    assert response.json() == {"error": "Problem occurred with json field date: Input should be a valid string"}


def test_handler_with_incorrect_format_of_date_field():
    """Request with wrong input for data field, should be bad request"""
    response = client.post("/calculate", json={"date": "17/11/2023", "periods": 10, "amount": 100000, "rate": 3.9})
    assert response.status_code == 400
    assert response.json() == {"error": "Problem occurred with json field date: String should match pattern '^\\d{"
                                        "2}\\.\\d{2}\\.\\d{4}$'"}


def test_handler_with_date_field_that_dont_exist():
    """Request with date that cannot exist, should be bad request"""
    response = client.post("/calculate", json={"date": "32.11.2023", "periods": 10, "amount": 100000, "rate": 3.9})
    assert response.status_code == 400
    assert response.json() == {"error": "Problem occurred with json field date: Date cannot exist."}


def test_function_that_check_correctness_of_date_with_correct_value():
    """Call of check_correctness_of_date function with correct value"""
    assert check_correctness_of_date("28.02.2025") == datetime.datetime(day=28, month=2, year=2025)


def test_function_that_check_correctness_of_date_with_incorrect_format_of_date():
    """Call of check_correctness_of_date function with incorrect format of date"""
    assert check_correctness_of_date("28/02/2025") is None


def test_function_that_check_correctness_of_date_with_date_that_doesnt_exist():
    """Call of check_correctness_of_date function with date that cannot exist"""
    assert check_correctness_of_date("29.02.2025") is None


def test_deposit_algorithm_function_basic():
    """Call of deposit_algorithm function to get payment periods"""
    needed_result = {"28.02.2021": 10050.0, "31.03.2021": 10100.25, "30.04.2021": 10150.75125}
    assert deposit_algorithm(datetime.datetime(day=31, month=1, year=2021), 3, 10000, 6) == needed_result


def test_deposit_algorithm_function_stress():
    """Call of deposit_algorithm function to get payment periods"""
    needed_result = {
        "29.02.2024": 1006416.6666666666,
        "31.03.2024": 1012874.5069444444,
        "30.04.2024": 1019373.7850306713,
        "31.05.2024": 1025914.7668179515,
        "30.06.2024": 1032497.7199050334,
        "31.07.2024": 1039122.9136077573,
        "31.08.2024": 1045790.6189700738,
        "30.09.2024": 1052501.1087751316,
        "31.10.2024": 1059254.6575564388,
        "30.11.2024": 1066051.5416090926,
        "31.12.2024": 1072892.0390010844,
        "31.01.2025": 1079776.4295846748,
        "28.02.2025": 1086704.995007843,
        "31.03.2025": 1093678.01872581,
        "30.04.2025": 1100695.7860126342,
        "31.05.2025": 1107758.583972882,
        "30.06.2025": 1114866.7015533748,
        "31.07.2025": 1122020.429555009,
        "31.08.2025": 1129220.0606446536,
        "30.09.2025": 1136465.8893671236,
        "31.10.2025": 1143758.2121572292,
        "30.11.2025": 1151097.3273519047,
        "31.12.2025": 1158483.5352024129,
        "31.01.2026": 1165917.1378866283,
        "28.02.2026": 1173398.4395214007,
        "31.03.2026": 1180927.7461749965,
        "30.04.2026": 1188505.3658796195,
        "31.05.2026": 1196131.6086440138,
        "30.06.2026": 1203806.7864661461,
        "31.07.2026": 1211531.2133459705,
        "31.08.2026": 1219305.2052982738,
        "30.09.2026": 1227129.0803656045,
        "31.10.2026": 1235003.1586312838,
        "30.11.2026": 1242927.7622325013,
        "31.12.2026": 1250903.2153734933,
        "31.01.2027": 1258929.8443388066,
        "28.02.2027": 1267007.9775066474,
        "31.03.2027": 1275137.945362315,
        "30.04.2027": 1283320.0805117232,
        "31.05.2027": 1291554.7176950066,
        "30.06.2027": 1299842.1938002163,
        "31.07.2027": 1308182.847877101,
        "31.08.2027": 1316577.0211509792,
        "30.09.2027": 1325025.057036698,
        "31.10.2027": 1333527.3011526836,
        "30.11.2027": 1342084.1013350799,
        "31.12.2027": 1350695.80765198,
        "31.01.2028": 1359362.772417747,
        "29.02.2028": 1368085.3502074275,
        "31.03.2028": 1376863.8978712584,
        "30.04.2028": 1385698.7745492656,
        "31.05.2028": 1394590.3416859568,
        "30.06.2028": 1403538.9630451084,
        "31.07.2028": 1412545.0047246478,
        "31.08.2028": 1421608.835171631,
        "30.09.2028": 1430730.8251973158,
        "31.10.2028": 1439911.347992332,
        "30.11.2028": 1449150.7791419495,
        "31.12.2028": 1458449.4966414436,
        "31.01.2029": 1467807.8809115596
    }
    assert deposit_algorithm(datetime.datetime(day=31, month=1, year=2024), 60, 1000000, 7.7) == needed_result
