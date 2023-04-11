import datetime
import json
import random
from pprint import pprint

import pytest
import requests
from combidata import *
from combidata.classes.combination import Combination
from re_generate import re_generate

from test import agent_code


def full_dict_compare(left, right):
    if left != right:
        return False
    for key, value in left.items():
        if value != right[key]:
            print(value, right[key])
            return False
    return True


def generate_date(args_dict):
    """
    Функция генерирует дату на основе переданных аргументов
    Возвращает строку в формате 'ДД.ММ.ГГГГ'
    """

    anchor_date = args_dict.get('anchor_date', None)
    other_date = args_dict.get('other_date', None)
    days = args_dict.get('days', 0)
    months = args_dict.get('months', 0)
    years = args_dict.get('years', 0)
    form = args_dict.get('form', '%d.%m.%Y')

    if not anchor_date:
        anchor_date = datetime.date.today()
    if isinstance(anchor_date, str):
        anchor_date = datetime.datetime.strptime(anchor_date, '%d.%m.%Y').date()

    if not isinstance(anchor_date, datetime.date):
        raise ValueError('Некорректный формат опорной даты')

    year = anchor_date.year + years
    month = anchor_date.month + months
    day = anchor_date.day + days

    if month <= 0:
        year -= 1
        month += 12

    days_in_month = {
        1: 31,
        2: 28 if year % 4 != 0 or (year % 100 == 0 and year % 400 != 0) else 29,
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31
    }

    while day <= 0:
        month -= 1
        if month <= 0:
            year -= 1
            month += 12
        day += days_in_month[month]

    while day > days_in_month[month]:
        day -= days_in_month[month]
        month += 1
        if month > 12:
            year += 1
            month -= 12

    generated_date = datetime.date(year, month, day) if other_date is None else other_date

    max_date = anchor_date if anchor_date > generated_date else generated_date
    min_date = anchor_date if max_date == generated_date else generated_date

    if min_date == max_date:
        return datetime.date.today().strftime(form)

    delta_days = random.randint(1, (max_date - min_date).days)

    return (max_date - datetime.timedelta(delta_days)).strftime(form)


def export(combination: Combination):
    pprint(combination.formed_data)
    sent_request = json.dumps(combination.formed_data)
    received_json = requests.post("http://localhost/send", headers={"agent": agent_code}, data=sent_request).text
    combination.cache.update({"received_json": json.loads(received_json)})
    pprint(combination.cache["received_json"])
    return True


def ask(combination: Combination):
    sent_request = json.dumps(combination.cache["received_json"])
    received_json = requests.post("http://localhost/receive", headers={"agent": agent_code}, data=sent_request).text
    combination.cache.update({"saved_data": json.loads(received_json)})
    pprint(json.loads(received_json))
    return True


def compare(combination: Combination):
    del combination.cache["saved_data"]["TARGETID"]
    if combination.cache["saved_data"] != combination.formed_data:
        combination.cache.update({"result": False})
        return True
    combination.cache.update({"result": True})
    return True


def er_compare(combination: Combination):
    if combination.cache["received_json"] != combination.main_case.additional_fields["error"]:
        combination.cache.update({"result": False})
        return True
    combination.cache.update({"result": True})
    return True


EXPORT = Process("EXPORT", export)
ASK = Process("ASK", ask)
COMPARE = Process("COMPARE", compare)
ER_COMPARE = Process("ER_COMPARE", er_compare)

library = {
    "cases": {},
    "workflow": {"standard": (ST_COMBINE, ST_GENERATE, ST_FORM, EXPORT, ASK, COMPARE),
                 "error": (ST_COMBINE, ST_GENERATE, ST_FORM, EXPORT, ER_COMPARE)},
    "tools": {},
    "template": {}
}

library["cases"]["BALANCE"] = {
    "Correct": {
        "value": r"[1-9][0-9]{0,8}.[0-9]{2}|0.[0-9]{2}",
        "gen_func": re_generate,
        "name": "Проверка поля BALANCE на корректное значение"
    },
    "None": {
        "is_presented": False,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле BALANCE"},
        "name": "Проверка поля BALANCE на присутствие ошибки по обязательности поля"
    },
    "NCorrectValue": {
        "value": r"[1-9][0-9]{9,20}.[0-9]{2}|0.[0-9]{3,10}",
        # [1-9][0-9]{9,20}.[0-9]{2}|0[0-9]{0,8}.[0-9]{2}|0.[0-9]{3,10}
        "gen_func": re_generate,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле BALANCE"},
        "name": "Проверка поля BALANCE на присутствие ошибки по некорректному значению"
    },
    "NCorrectSy": {
        "value": r"[A-Za-z]{1,5}",
        "gen_func": re_generate,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле BALANCE"},
        "name": "Проверка поля BALANCE на присутствие ошибки по некорректным символам"
    },
}
library["cases"]["BANK_ACCOUNT"] = {
    "Correct": {
        "value": r"[0-9]{10}",
        "gen_func": re_generate,
        "name": "Проверка поля BANK_ACCOUNT на корректное значение"
    },
    "None": {
        "is_presented": False,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле BANK_ACCOUNT"},
        "name": "Проверка поля BANK_ACCOUNT на присутствие ошибки по обязательности поля"
    },
    "NCorrectValue": {
        "value": r"[0-9]{1,9}|[0-9]{11,15}",
        "gen_func": re_generate,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле BANK_ACCOUNT"},
        "name": "Проверка поля BANK_ACCOUNT на присутствие ошибки по некорректному значению"
    },
    "NCorrectSy": {
        "value": r"[A-Za-z]{1,5}",
        "gen_func": re_generate,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле BANK_ACCOUNT"},
        "name": "Проверка поля BANK_ACCOUNT на присутствие ошибки по некорректным символам"
    },
}
library["cases"]["BIRTHDATE"] = {
    "Correct": {
        "value": {"years": -14},
        "gen_func": generate_date,
        "name": "Проверка поля BIRTHDATE на корректное значение"
    },
    "None": {
        "is_presented": False,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле BIRTHDATE"},
        "name": "Проверка поля BIRTHDATE на присутствие ошибки по обязательности поля"
    },
    "NCorrectValue": {
        "value": {"years": 1},
        "gen_func": generate_date,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле BIRTHDATE"},
        "name": "Проверка поля BIRTHDATE на присутствие ошибки по некорректному значению"
    },
    "NCorrectSy": {
        "value": {"years": -14, "form": '%d-%m-%Y'},
        "gen_func": generate_date,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле BIRTHDATE"},
        "name": "Проверка поля BIRTHDATE на присутствие ошибки по некорректным символам"
    },
    "NotDate": {
        "value": r"[0-9]{8}",
        "gen_func": re_generate,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле BIRTHDATE"},
        "name": "Проверка поля BIRTHDATE на присутствие ошибки по не дате"
    },
}
library["cases"]["CAR_NO"] = {
    "Correct": {
        "value": r"[УКЕНХВАРОСМТYKEHXBAPOCMT][0-9]{3}[УКЕНХВАРОСМТYKEHXBAPOCMT]{2}[0-9]{2,3}|[УКЕНХВАРОСМТYKEHXBAPOCMT]{2}[0-9]{3}[УКЕНХВАРОСМТYKEHXBAPOCMT][0-9]{2}|[0-9]{4}[УКЕНХВАРОСМТYKEHXBAPOCMT]{2}[0-9]{2}|[УКЕНХВАРОСМТYKEHXBAPOCMT]{2}[0-9]{6}",
        "gen_func": re_generate,
        "name": "Проверка поля CAR_NO на корректное значение"
    },
    "None": {
        "is_presented": False,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле CAR_NO"},
        "name": "Проверка поля CAR_NO на присутствие ошибки по обязательности поля"
    },
    "NCorrectValue": {
        "value": r"[УКЕНХВАРОСМТYKEHXBAPOCMT][0-9]{3}",
        "gen_func": re_generate,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле CAR_NO"},
        "name": "Проверка поля CAR_NO на присутствие ошибки по некорректному значению"
    },
    "NCorrectSy": {
        "value": r"[A-Za-z]{1,5}",
        "gen_func": re_generate,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле CAR_NO"},
        "name": "Проверка поля CAR_NO на присутствие ошибки по некорректным символам"
    },
}
library["cases"]["FLAT"] = {
    "Correct": {
        "value": r"[0-9]{1,5}",
        "gen_func": re_generate,
        "name": "Проверка поля FLAT на корректное значение"
    },
    "None": {
        "is_presented": False,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле FLAT"},
        "name": "Проверка поля FLAT на присутствие ошибки по обязательности поля"
    },
    "NCorrectValue": {
        "value": r"[0-9]{6,10}",
        "gen_func": re_generate,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле FLAT"},
        "name": "Проверка поля FLAT на присутствие ошибки по некорректному значению"
    },
    "NCorrectSy": {
        "value": r"[A-Za-z]{1,5}",
        "gen_func": re_generate,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле FLAT"},
        "name": "Проверка поля FLAT на присутствие ошибки по некорректным символам"
    },
}
library["cases"]["HOUSE"] = {
    "Correct": {
        "value": r"[0-9]{1,5}",
        "gen_func": re_generate,
        "name": "Проверка поля HOUSE на корректное значение"
    },
    "None": {
        "is_presented": False,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле HOUSE"},
        "name": "Проверка поля HOUSE на присутствие ошибки по обязательности поля"
    },
    "NCorrectValue": {
        "value": r"[0-9]{6,10}",
        "gen_func": re_generate,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле HOUSE"},
        "name": "Проверка поля HOUSE на присутствие ошибки по некорректному значению"
    },
    "NCorrectSy": {
        "value": r"[A-Za-z]{1,5}",
        "gen_func": re_generate,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле HOUSE"},
        "name": "Проверка поля HOUSE на присутствие ошибки по некорректным символам"
    },
}
library["cases"]["ID_CARD"] = {
    "Correct": {
        "value": r"[0-9]{9}",
        "gen_func": re_generate,
        "name": "Проверка поля ID_CARD на корректное значение"
    },
    "None": {
        "is_presented": False,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле ID_CARD"},
        "name": "Проверка поля ID_CARD на присутствие ошибки по обязательности поля"
    },
    "NCorrectValue": {
        "value": r"[0-9]{10,15}",
        "gen_func": re_generate,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле ID_CARD"},
        "name": "Проверка поля ID_CARD присутствие ошибки по некорректному значению"
    },
    "NCorrectSy": {
        "value": r"[A-Za-z]{1,5}",
        "gen_func": re_generate,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле ID_CARD"},
        "name": "Проверка поля ID_CARD на присутствие ошибки по некорректным символам"
    },
}
library["cases"]["NAME"] = {
    "Correct": {
        "value": r"[А-ЯёЁа-яIVXLC\-']{1,50}",
        "gen_func": re_generate,
        "name": "Проверка поля NAME на корректное значение"
    },
    "None": {
        "is_presented": False,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле NAME"},
        "name": "Проверка поля NAME на присутствие ошибки по обязательности поля"
    },
    "NCorrectValue": {
        "value": r"[А-ЯёЁа-яIVXLC\-']{51,60}",
        "gen_func": re_generate,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле NAME"},
        "name": "Проверка поля NAME присутствие ошибки по некорректному значению"
    },
    "NCorrectSy": {
        "value": r"[a-z]{1,50}",
        "gen_func": re_generate,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле NAME"},
        "name": "Проверка поля NAME на присутствие ошибки по некорректным символам"
    },
}
library["cases"]["PASSPORT"] = {
    "Correct": {
        "value": r"[0-9]{2} [0-9]{2} [0-9]{6}",
        "gen_func": re_generate,
        "name": "Проверка поля PASSPORT на корректное значение"
    },
    "Noness": {
        "is_presented": False,
        "name": "Проверка поля PASSPORT на необязательность"
    },
    "None": {
        "is_presented": False,
        "type": "off",
        "error": {"ERROR": "Неправильно заполнено поле PASSPORT"},
        "name": "Проверка поля PASSPORT на присутствие ошибки по обязательности поля"
    },
    "NCorrectValue": {
        "value": r"[0-9]{10}|[0-9]{11,15}|[0-9]{1,9}",
        "gen_func": re_generate,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле PASSPORT"},
        "name": "Проверка поля PASSPORT присутствие ошибки по некорректному значению"
    },
    "NCorrectSy": {
        "value": r"[A-Za-z]{1,5}",
        "gen_func": re_generate,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле PASSPORT"},
        "name": "Проверка поля PASSPORT на присутствие ошибки по некорректным символам"
    },
}
library["cases"]["PASSPORT_ISSUE"] = {
    "Correct": {
        "value": {"years": -14},
        "gen_func": generate_date,
        "name": "Проверка поля PASSPORT_ISSUE на корректное значение"
    },
    "None": {
        "is_presented": False,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле PASSPORT_ISSUE"},
        "name": "Проверка поля PASSPORT_ISSUE на присутствие ошибки по обязательности поля"
    },
    "NCorrectValue": {
        "value": {"years": 1},
        "gen_func": generate_date,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле PASSPORT_ISSUE"},
        "name": "Проверка поля PASSPORT_ISSUE на присутствие ошибки по некорректному значению"
    },
    "NCorrectSy": {
        "value": {"years": -14, "form": '%d-%m-%Y'},
        "gen_func": generate_date,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле PASSPORT_ISSUE"},
        "name": "Проверка поля PASSPORT_ISSUE на присутствие ошибки по некорректным символам"
    },
    "NotDate": {
        "value": r"[0-9]{8}",
        "gen_func": re_generate,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле PASSPORT_ISSUE"},
        "name": "Проверка поля PASSPORT_ISSUE на присутствие ошибки по не дате"
    },
}
library["cases"]["POST_NO"] = {
    "Correct": {
        "value": r"[0-9]{3}\-[0-9]{3}",
        "gen_func": re_generate,
        "name": "Проверка поля POST_NO на корректное значение"
    },
    "None": {
        "is_presented": False,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле POST_NO"},
        "name": "Проверка поля POST_NO на присутствие ошибки по обязательности поля"
    },
    "NCorrectValue": {
        "value": r"[0-9]{6}",
        "gen_func": re_generate,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле POST_NO"},
        "name": "Проверка поля POST_NO присутствие ошибки по некорректному значению"
    },
    "NCorrectSy": {
        "value": r"[A-Za-z]{1,5}",
        "gen_func": re_generate,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле POST_NO"},
        "name": "Проверка поля POST_NO на присутствие ошибки по некорректным символам"
    },
}
library["cases"]["STREET"] = {
    "Correct": {
        "value": r"[А-ЯёЁа-я0-9IVXLC\-']{1,50}",
        "gen_func": re_generate,
        "name": "Проверка поля STREET на корректное значение"
    },
    "None": {
        "is_presented": False,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле STREET"},
        "name": "Проверка поля STREET на присутствие ошибки по обязательности поля"
    },
    "NCorrectValue": {
        "value": r"[А-ЯёЁа-я0-9IVXLC\-']{51,60}",
        "gen_func": re_generate,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле STREET"},
        "name": "Проверка поля STREET присутствие ошибки по некорректному значению"
    },
    "NCorrectSy": {
        "value": r"[a-z]{1,5}",
        "gen_func": re_generate,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле STREET"},
        "name": "Проверка поля STREET на присутствие ошибки по некорректным символам"
    },
}
library["cases"]["SURNAME"] = {
    "Correct": {
        "value": r"[А-ЯёЁа-я]{1,50}",
        "gen_func": re_generate,
        "name": "Проверка поля SURNAME на корректное значение"
    },
    "None": {
        "is_presented": False,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле SURNAME"},
        "name": "Проверка поля SURNAME на присутствие ошибки по обязательности поля"
    },
    "NCorrectValue": {
        "value": r"[А-ЯёЁа-я]{51,60}",
        "gen_func": re_generate,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле SURNAME"},
        "name": "Проверка поля SURNAME присутствие ошибки по некорректному значению"
    },
    "NCorrectSy": {
        "value": r"[A-Za-z]{1,5}",
        "gen_func": re_generate,
        "type": "error",
        "error": {"ERROR": "Неправильно заполнено поле SURNAME"},
        "name": "Проверка поля SURNAME на присутствие ошибки по некорректным символам"
    },
}
library["template"] = {field: field for field in library["cases"].keys()}

#generator = DataGenerator(library, amount=100)
generator = DataGenerator(library, type_of_cases="error", amount=100)


@pytest.mark.parametrize("combination_name", generator.combinations.keys())
def test(combination_name):
    combination = generator.combinations[combination_name]
    combination.run()
    assert combination.cache["result"]
