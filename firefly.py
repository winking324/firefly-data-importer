# -*- coding: utf-8 -*-
__author__ = "winking324@gmail.com"
__copyright__ = "Copyright (c) 2014-2017 winking324."

import http
import requests


TOKEN = """这里填写你的“个人访问令牌”"""
HEADERS = {
    "Authorization": "Bearer {}".format(TOKEN),
    "accept": "application/vnd.api+json",
    "Content-Type": "application/json",
}


def create_account(port, data):
    try:
        response = requests.post(
            url="http://localhost:{}/api/v1/accounts".format(port),
            headers=HEADERS,
            data=data
        )
        if response.status_code != http.HTTPStatus.OK:
            print('Error: update account failed, {}'.format(response.content.decode('unicode_escape')))
            return False, None
        return True, response.content
    except requests.exceptions.RequestException as e:
        print('Error: update account failed, {}'.format(repr(e)))
        return False, None


def create_transactions(port, data):
    try:
        response = requests.post(
            url="http://localhost:{}/api/v1/transactions".format(port),
            headers=HEADERS,
            data=data
        )
        if response.status_code != http.HTTPStatus.OK:
            print('Error: create transaction failed, {}'.format(response.content.decode('unicode_escape')))
            return False
        return True
    except requests.exceptions.RequestException as e:
        print('Error: update account failed, {}'.format(repr(e)))
        return False
