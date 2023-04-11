import copy
import json

import pytest
import requests

true_data = {"STREET": "Алебановская",
             "HOUSE": "32345",
             "BALANCE": "11040.30",
             "BANK_ACCOUNT": "674342",
             "FLAT": "123",
             "CAR_NO": "У123УУ12",
             "PASSPORT": "45 55 678902",
             "BIRTHDATE": "12.12.1990",
             "ID_CARD": "123456789",
             "POST_NO": "107-607",
             "PASSPORT_ISSUE": "12.12.1990",
             "NAME": "Alex",
             "SURNAME": "йцукенгшщзйцукенгшщзйцукенгшщзйцукенгшщзйцукенгш"}

false_data = {
    "STREET": ["Petrov", "Dedkov"],
    "HOUSE": ["дом", "12345678", "абв"],
    "BALANCE": [".45"],
    "BANK_ACCOUNT": ["О0O", "АА25", "123456789101112", "4546 4646"],
    "FLAT": ["дом", "12345678", "абв"],
    "CAR_NO": ["T479КD777", "А036"],
    "PASSPORT": ["АА ВВ 178657"],
    "BIRTHDATE": ["01.02.20", "09.04.2023", "05.05.23"],
    "ID_CARD": ["11111111111", "AA12BB13"],
    "POST_NO": ["99D-000", "00-000"],
    "PASSPORT_ISSUE": ["01.02.20", "09.04.2023", "05.05.23"],
    "NAME": ["Иванов", "qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq"],
    "SURNAME": ["Petrov", "Dedkov", "йцукенгшщзйцукенгшщзйцукенгшщзйцукенгшщзйцукенгшукенгш"]}

resp = requests.post("http://10.36.201.57/send", headers={"agent": "AB122I", "Content-Type": "application/json"},
                     data=json.dumps(true_data))
print(resp.text)


def test_fix():
    resp = requests.get("http://10.36.201.57/end", headers={"agent": "AB122I", "Content-Type": "application/json"})
    jsoned_resp = json.loads(resp.text)
    print(jsoned_resp)


def test_true():
    resp = requests.post("http://10.36.201.57/send", headers={"agent": "AB122I", "field": "application/json"},
                         data=json.dumps(true_data))
    jsoned_resp = json.loads(resp.text)
    print()
    print(jsoned_resp)
    a = jsoned_resp["TARGET_ID"]
    resp = requests.post("http://10.36.201.57/receive", headers={"agent": "AB122I", "field": "application/json"},
                         data=resp.text)
    jsoned_resp = json.loads(resp.text)
    print()
    print(jsoned_resp)

formed_corrupted_data = []
for key, value in false_data.items():
    for item in value:
        formed_corrupted_data.append([key, item])

@pytest.mark.parametrize("key,test",formed_corrupted_data)
def test_false(key, test):
    data = copy.deepcopy(true_data)
    data[key] = test
    resp = requests.post("http://10.36.201.57/send", headers={"agent": "AB122I", "field": "application/json"},
                         data=json.dumps(data))
    jsoned_resp = json.loads(resp.text)
    print()
    print(jsoned_resp)
    a = jsoned_resp["ERROR"]
    print(a)
