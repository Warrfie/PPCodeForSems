import copy
import json
from pprint import pprint

import pytest
import requests

agent_code = "AB122I"
# print(requests.get("http://localhost/").text)
# print(requests.get("http://localhost/", headers={"agent": agent_code}).text)

export_data = {
    "STREET": "Алебановская-'VX",
    "HOUSE": "3",
    "BALANCE": "11040.30",
    "BANK_ACCOUNT": "1234567890",
    "FLAT": "123",
    "CAR_NO": "XX000000",
    "PASSPORT": "12 34 567890",
    "BIRTHDATE": "12.12.1990",
    "ID_CARD": "012345678",
    "POST_NO": "107-607",
    "PASSPORT_ISSUE": "12.12.1990",
    "NAME": "qwaswqaszsaqweasfesdewsdewsdewsdewsdewsde",
    "SURNAME": "Иванов"}
dumped_data = json.dumps(export_data)

corrupted_data = {
    "STREET": ["Алебановскаяeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee", "f1"],
    "HOUSE": ["", "123456", "addw"],
    "BALANCE": ["110400000000000000000000000000000000000.30", "10.00030"],
    "BANK_ACCOUNT": ["12345678901","1", "d123456789"],
    "FLAT": ["123456", "", "f"],
    "CAR_NO": ["УУ123УУ12", "У12УУ12", "123", "У12УУ"],
    "PASSPORT": ["1234567890", "1", ""],
    "BIRTHDATE": ["12-12-1990", "1990", "12.12.2990"],
    "ID_CARD": ["5545555550", "12345678o"],
    "POST_NO": ["107607", "107607-"],
    "PASSPORT_ISSUE": ["12-12-1990", "1990", "12.12.2990"],
    "NAME": ["Иванов", "1a", "sы", "", "qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq"],
    "SURNAME": ["вв1", "aa", "", "Алебановскаяeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"]}

formed_corrupted_data = []
for key, value in corrupted_data.items():
    for item in value:
        formed_corrupted_data.append([key, item])


def test_true():
    data = copy.deepcopy(export_data)
    dumped_data = json.dumps(data)
    received_data = requests.post("http://localhost/send", headers={"agent": agent_code}, data=dumped_data).text
    jsoned_data = json.loads(received_data)
    pprint(jsoned_data)
    assert bool(jsoned_data.get('TARGET_ID', False))

def test_STREET1():
    data = copy.deepcopy(export_data)
    data["HOUSE"] = ""
    dumped_data = json.dumps(data)
    received_data = requests.post("http://localhost/send", headers={"agent": agent_code}, data=dumped_data).text
    jsoned_data = json.loads(received_data)
    pprint(jsoned_data)
    assert not bool(jsoned_data.get('TARGET_ID', False))

def test_STREET2():
    data = copy.deepcopy(export_data)
    data["HOUSE"] = "232344"
    dumped_data = json.dumps(data)
    received_data = requests.post("http://localhost/send", headers={"agent": agent_code}, data=dumped_data).text
    jsoned_data = json.loads(received_data)
    pprint(jsoned_data)
    assert not bool(jsoned_data.get('TARGET_ID', False))

def test_STREET3():
    data = copy.deepcopy(export_data)
    data["HOUSE"] = "23234a"
    dumped_data = json.dumps(data)
    received_data = requests.post("http://localhost/send", headers={"agent": agent_code}, data=dumped_data).text
    jsoned_data = json.loads(received_data)
    pprint(jsoned_data)
    assert not bool(jsoned_data.get('TARGET_ID', False))

def test_BALANCE1():
    data = copy.deepcopy(export_data)
    data["BALANCE"] = "123456666666666666666"
    dumped_data = json.dumps(data)
    received_data = requests.post("http://localhost/send", headers={"agent": agent_code}, data=dumped_data).text
    jsoned_data = json.loads(received_data)
    pprint(jsoned_data)
    assert not bool(jsoned_data.get('TARGET_ID', False))


def test_BANK_ACCOUNT1():
    data = copy.deepcopy(export_data)
    data["BANK_ACCOUNT"] = "123456666666666666666"
    dumped_data = json.dumps(data)
    received_data = requests.post("http://localhost/send", headers={"agent": agent_code}, data=dumped_data).text
    jsoned_data = json.loads(received_data)
    pprint(jsoned_data)
    assert not bool(jsoned_data.get('TARGET_ID', False))

def test_BANK_ACCOUNT2():
    data = copy.deepcopy(export_data)
    data["BANK_ACCOUNT"] = "123456789a"
    dumped_data = json.dumps(data)
    received_data = requests.post("http://localhost/send", headers={"agent": agent_code}, data=dumped_data).text
    jsoned_data = json.loads(received_data)
    pprint(jsoned_data)
    assert not bool(jsoned_data.get('TARGET_ID', False))


@pytest.mark.parametrize("key,test",formed_corrupted_data)
def test_util(key, test):
    print()
    print(key, test)
    data = copy.deepcopy(export_data)
    data[key] = test
    pprint(data)
    dumped_data = json.dumps(data)
    received_data = requests.post("http://localhost/send", headers={"agent": agent_code}, data=dumped_data).text
    jsoned_data = json.loads(received_data)
    pprint(jsoned_data)
    saved = bool(jsoned_data.get('TARGET_ID', False))
    assert not saved and key in jsoned_data.get('ERROR', False)