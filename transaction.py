# -*- coding: utf-8 -*-
__author__ = "winking324@gmail.com"
__copyright__ = "Copyright (c) 2014-2017 winking324."

import enum
import json
import re
import pandas


class TransactionType(enum.Enum):
    WITHDRAWAL = 'withdrawal'  # 支出
    DEPOSIT = 'deposit'  # 收入
    TRANSFER = 'transfer'  # 转账
    RECONCILIATION = 'reconciliation'
    OPENING_BALANCE = 'opening_balance'  # 期初余额


class Transaction:
    def __init__(self):
        self.type = ''  # 交易类型
        self.date = ''  # 交易时间，格式：2018-09-17T12:46:47+01:00
        self.amount = ''  # 交易金额
        self.description = ''  # 交易描述
        self.category_name = None  # 分类名称
        self.source_id = None  # 交易账户 ID
        self.source_name = None  # 交易账户名称
        self.destination_id = None  # 交易对方 ID
        self.destination_name = None  # 交易对方名称
        self.tags = None  # 标签

    def update_amount(self, amount):
        currency = re.sub(r'[^\d.-]', '', amount)
        if float(currency) < 0:
            self.type = TransactionType.WITHDRAWAL.value
        else:
            self.type = TransactionType.DEPOSIT.value
        self.amount = currency

    def parse(self, message):
        self.source_name = message[3]
        if pandas.isna(message[10]):
            print('Error: Transaction currency error, {}'.format(message))
            return False
        self.update_amount(message[10])

        if not pandas.isna(message[8]) and not pandas.isna(message[9]):
            self.date = '{}T{}:00+08:00'.format(message[8], message[9])
        else:
            print('Error: Transaction date error, {}'.format(message))
            return False

        if not pandas.isna(message[4]):
            self.type = TransactionType.TRANSFER.value
            self.destination_name = message[4]
            if float(self.amount) > 0:
                self.source_name, self.destination_name = self.destination_name, self.source_name
        elif not pandas.isna(message[6]):
            self.destination_name = message[6]
        else:
            if not pandas.isna(message[5]) and message[5] == '新余额':
                self.destination_name = '余额调整'
            else:
                print('Warning: Transaction not found destination, {}'.format(message))
                return False
        self.amount = self.amount.replace('-', '')
        if self.type is TransactionType.DEPOSIT.value:
            self.source_name, self.destination_name = self.destination_name, self.source_name
        if not pandas.isna(message[5]):
            self.description = message[5]

        if not pandas.isna(message[7]):
            tags = message[7].split(' ▶︎ ')
            self.category_name = tags[0]
            self.tags = tags
        return True

    def to_json(self):
        return json.dumps(self,
                          default=lambda o: dict((key, value) for key, value in o.__dict__.items() if value),
                          allow_nan=False)
