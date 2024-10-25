# -*- coding: utf-8 -*-
__author__ = "winking324@gmail.com"
__copyright__ = "Copyright (c) 2014-2017 winking324."

import datetime
import enum
import re
import json
import decimal
import pandas

import firefly
import transaction


class AccountType(enum.Enum):
    ASSET = 'asset'  # 资产
    EXPENSE = 'expense'  # 支出
    REVENUE = 'revenue'  # 收入
    CASH = 'cash'  # 钱包
    LIABILITY = 'liability'  # 债务
    LIABILITIES = 'liabilities'  # 债务？


class AccountRoleType(enum.Enum):
    DEFAULT = 'defaultAsset'  # 默认
    SHARED = 'sharedAsset'  # 共用
    SAVING = 'savingAsset'  # 储蓄
    CC = 'ccAsset'  # 信用
    cash_wallet = 'cashWalletAsset'  # 现金钱包


class Account:
    def __init__(self):
        self.id = None
        self.name = None
        self.type = AccountType.ASSET.value
        self.opening_balance = None
        self.opening_balance_date = None
        self.account_role_type = AccountRoleType.SAVING.value
        self.transactions = []

    def __update_opening_balance(self, transaction_item):
        if transaction_item.type is transaction.TransactionType.WITHDRAWAL.value:
            self.opening_balance += decimal.Decimal(transaction_item.amount)
        elif transaction_item.type is transaction.TransactionType.TRANSFER.value:
            if self.name == transaction_item.source_name:
                self.opening_balance += decimal.Decimal(transaction_item.amount)
            else:
                self.opening_balance -= decimal.Decimal(transaction_item.amount)
        else:
            self.opening_balance -= decimal.Decimal(transaction_item.amount)

    def parse_account(self, message):
        self.name = message[1]
        self.opening_balance = decimal.Decimal(re.sub(r'[^\d.-]', '', message[2]))
        if self.opening_balance < 0:
            self.account_role_type = AccountRoleType.CC.value

        if not pandas.isna(message[8]) and not pandas.isna(message[9]):
            self.opening_balance_date = '{}T{}:00+08:00'.format(message[8], message[9])
        return True

    def parse_transaction(self, message):
        new_transaction = transaction.Transaction()
        if not new_transaction.parse(message):
            return False

        if not self.opening_balance_date:
            self.opening_balance_date = new_transaction.date
        else:
            old_date = pandas.to_datetime(self.opening_balance_date)
            new_date = pandas.to_datetime(new_transaction.date)
            if new_date < old_date:
                self.opening_balance_date = new_transaction.date
        self.__update_opening_balance(new_transaction)
        self.transactions.append(new_transaction)
        return True

    def create_account(self, port):
        if not self.opening_balance_date:
            self.opening_balance_date = datetime.datetime.now().strftime('%Y/%m/%dT%H:%M:00+08:00')
        data = {
            'name': self.name,
            'type': self.type,
            'opening_balance': str(self.opening_balance),
            'opening_balance_date': self.opening_balance_date,
            'account_role': self.account_role_type
        }
        if self.account_role_type is AccountRoleType.CC.value:
            data['credit_card_type'] = 'monthlyFull'
            data['monthly_payment_date'] = self.opening_balance_date
        res, res_data = firefly.create_account(port, json.dumps(data))
        if not res or not res_data:
            return False
        account_info = json.loads(res_data)
        self.id = account_info['data']['id']
        return True

    def create_transactions(self, port, accounts):
        for transaction_item in self.transactions:
            # 忽略其他 Account 对该 Account 的转账，否则相同转账信息会存在 2 份
            if (transaction_item.type is transaction.TransactionType.TRANSFER and
                    transaction_item.source_name != self.name):
                continue

            if transaction_item.source_name in accounts:
                transaction_item.source_id = accounts[transaction_item.source_name]
            if transaction_item.destination_name in accounts:
                transaction_item.destination_id = accounts[transaction_item.destination_name]
            data = '{{"transactions": [{}]}}'.format(transaction_item.to_json())
            if not firefly.create_transactions(port, data):
                print('Warning: create transaction {} failed, ignored, please create it by yourself'.format(data))
                continue
        return True
